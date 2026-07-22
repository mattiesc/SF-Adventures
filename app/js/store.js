// Storage layer. Two interchangeable backends behind one interface:
//   - FirebaseStore: shared household deck synced live via Firestore + Google sign-in
//   - LocalStore:    per-device deck in localStorage (used until Firebase is configured)
//
// Interface both expose:
//   store.mode                      -> "local" | "firebase"
//   store.onChange(cb)              -> cb({deck, log}) on every state change
//   store.onAuth(cb)                -> cb({status, user, household}) for the connection banner
//   await store.init()
//   await store.applyAction(id, kind, untilMs)   // kind: "done" | "skip"
//   await store.reset()
//   await store.signIn() / signOut()             // firebase only (no-ops in local)
//   await store.addMember(email) / createHousehold()  // firebase only

import { firebaseConfig, isLocalMode } from "./config.js";

const LS_KEY = "sfadv_deck_v1";

// ── Local backend ────────────────────────────────────────────────────────────
function LocalStore() {
  let state = load();
  const subs = new Set();
  function load() {
    try { return JSON.parse(localStorage.getItem(LS_KEY)) || { deck: {}, log: [] }; }
    catch { return { deck: {}, log: [] }; }
  }
  function persist() {
    try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch {}
    subs.forEach((cb) => cb(state));
  }
  return {
    mode: "local",
    onChange(cb) { subs.add(cb); cb(state); return () => subs.delete(cb); },
    onAuth(cb) { cb({ status: "local" }); return () => {}; },
    async init() {},
    async applyAction(id, kind, untilMs) {
      state.deck[id] = { until: untilMs, kind, at: Date.now() };
      if (kind === "done") state.log = [{ id, at: Date.now() }, ...state.log].slice(0, 200);
      persist();
    },
    async reset() { state = { deck: {}, log: [] }; persist(); },
    async signIn() {}, async signOut() {},
    async createHousehold() {}, async addMember() {},
  };
}

// ── Firebase backend ─────────────────────────────────────────────────────────
async function FirebaseStore() {
  const [{ initializeApp }, authMod, fsMod] = await Promise.all([
    import("https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js"),
    import("https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js"),
    import("https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js"),
  ]);
  const {
    getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
  } = authMod;
  const {
    getFirestore, collection, query, where, getDocs, doc, getDoc, setDoc,
    updateDoc, onSnapshot, serverTimestamp, arrayUnion,
  } = fsMod;

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const db = getFirestore(app);

  let state = { deck: {}, log: [] };
  let user = null;
  let household = null;      // { id, members }
  let unsubDoc = null;
  const dataSubs = new Set();
  const authSubs = new Set();

  const emitData = () => dataSubs.forEach((cb) => cb(state));
  const emitAuth = (status) => authSubs.forEach((cb) => cb({ status, user, household }));

  function watchHousehold(id) {
    if (unsubDoc) unsubDoc();
    unsubDoc = onSnapshot(doc(db, "households", id), (snap) => {
      const d = snap.data() || {};
      state = { deck: d.deck || {}, log: d.log || [] };
      household = { id, members: d.members || [] };
      emitData();
      emitAuth("ready");
    });
  }

  async function findHousehold(email) {
    const q = query(collection(db, "households"), where("members", "array-contains", email));
    const res = await getDocs(q);
    return res.empty ? null : res.docs[0].id;
  }

  onAuthStateChanged(auth, async (u) => {
    user = u ? { uid: u.uid, email: (u.email || "").toLowerCase(), name: u.displayName } : null;
    if (unsubDoc) { unsubDoc(); unsubDoc = null; }
    if (!user) { household = null; state = { deck: {}, log: [] }; emitData(); emitAuth("signed-out"); return; }
    emitAuth("signing-in");
    const id = await findHousehold(user.email);
    if (id) { watchHousehold(id); }
    else { household = null; emitAuth("no-household"); }
  });

  return {
    mode: "firebase",
    onChange(cb) { dataSubs.add(cb); cb(state); return () => dataSubs.delete(cb); },
    onAuth(cb) { authSubs.add(cb); cb({ status: user ? "ready" : "signed-out", user, household }); return () => authSubs.delete(cb); },
    async init() {},
    async signIn() {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    },
    async signOut() { await signOut(auth); },
    async createHousehold() {
      if (!user) throw new Error("Sign in first");
      const id = "hh_" + user.uid.slice(0, 10) + "_" + Math.random().toString(36).slice(2, 8);
      await setDoc(doc(db, "households", id), {
        members: [user.email], createdBy: user.email, createdAt: serverTimestamp(),
        deck: {}, log: [],
      });
      watchHousehold(id);
    },
    async addMember(email) {
      if (!household) throw new Error("No household");
      await updateDoc(doc(db, "households", household.id), {
        members: arrayUnion(email.trim().toLowerCase()),
      });
    },
    async applyAction(id, kind, untilMs) {
      if (!household) return;
      const ref = doc(db, "households", household.id);
      const update = { [`deck.${id}`]: { until: untilMs, kind, by: user.email, at: Date.now() } };
      if (kind === "done") {
        const cur = (await getDoc(ref)).data() || {};
        const log = [{ id, at: Date.now(), by: user.email }, ...(cur.log || [])].slice(0, 200);
        update.log = log;
      }
      await updateDoc(ref, update);
    },
    async reset() {
      if (!household) return;
      await updateDoc(doc(db, "households", household.id), { deck: {}, log: [] });
    },
  };
}

export async function createStore() {
  if (isLocalMode) return LocalStore();
  try { return await FirebaseStore(); }
  catch (e) {
    console.error("Firebase init failed, falling back to local:", e);
    const s = LocalStore();
    s.initError = e;
    return s;
  }
}
