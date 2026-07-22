import {
  DAY, DEFAULT_COOLDOWNS, cooldownUntil, eligible, drawOne,
  restingList, fmtWhen, isResting,
} from "./deck.js";
import { createStore } from "./store.js";

const CATVAR = {
  "Outdoorsy & scenic": "--cat-out", "Food & drink": "--cat-food",
  "Arts & culture": "--cat-arts", "Playful & active": "--cat-play",
};
const TIMELBL = { "1hr": "~1 hr", "4hr": "~4 hrs", "all-day": "All day", "multi-day": "Getaway" };
const IOLBL = { indoor: "Indoor", outdoor: "Outdoor", mixed: "Indoor + out" };
const SCOPELBL = { "day-trip": "Day trip", getaway: "Getaway" };
const CATS = ["Outdoorsy & scenic", "Food & drink", "Arts & culture", "Playful & active"];

const el = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let ACT = [], BYID = {}, CFG = DEFAULT_COOLDOWNS, store = null;
let data = { deck: {}, log: [] };
let auth = { status: "local" };
let ui = { tab: "today", time: "surprise", near: false, current: null,
           bTime: "surprise", bCost: "all", bScope: "all", bCat: new Set(), bNear: false, q: "" };

// ── boot ─────────────────────────────────────────────────────────────────────
(async function boot() {
  const res = await fetch("./activities.json");
  const json = await res.json();
  ACT = json.activities;
  BYID = Object.fromEntries(ACT.map((a) => [a.id, a]));
  if (json.meta && json.meta.deck) CFG = { doCooldownDays: json.meta.deck.doCooldownDays, skipCooldownDays: json.meta.deck.skipCooldownDays };

  store = await createStore();
  store.onChange((s) => { data = s; renderMain(); renderStats(); });
  store.onAuth((a) => { auth = a; renderBanner(); if (ui.tab === "settings") renderMain(); });
  await store.init();

  wireChrome();
  renderBanner();
  renderMain();
})();

// ── top chrome: tabs + connection banner ──────────────────────────────────────
function wireChrome() {
  document.querySelectorAll(".tab").forEach((t) =>
    (t.onclick = () => { ui.tab = t.dataset.tab; ui.current = null;
      document.querySelectorAll(".tab").forEach((x) => x.setAttribute("aria-selected", x === t));
      renderMain(); }));
}

function renderBanner() {
  const b = el("banner");
  if (!b) return;
  if (store && store.mode === "local") {
    b.innerHTML = `<span class="dot warn"></span> Local mode — saved on this device only. <a href="#" data-goto="settings">Set up sharing</a>`;
  } else if (auth.status === "signed-out" || auth.status === "signing-in") {
    b.innerHTML = `<span class="dot warn"></span> Not signed in. <a href="#" data-goto="settings">Sign in to sync</a>`;
  } else if (auth.status === "no-household") {
    b.innerHTML = `<span class="dot warn"></span> Signed in — no shared deck yet. <a href="#" data-goto="settings">Create one</a>`;
  } else if (auth.status === "ready") {
    const n = auth.household ? auth.household.members.length : 0;
    b.innerHTML = `<span class="dot ok"></span> Synced${auth.user ? " as " + esc(auth.user.email) : ""} · ${n} in your deck`;
  } else if (auth.status === "error") {
    b.innerHTML = `<span class="dot warn"></span> ${esc(auth.error || "Something went wrong")} · <a href="#" data-goto="settings">Settings</a>`;
  } else {
    b.innerHTML = `<span class="dot"></span> Connecting…`;
  }
  b.querySelectorAll("a[data-goto]").forEach((a) => (a.onclick = (e) => {
    e.preventDefault(); ui.tab = a.dataset.goto;
    document.querySelectorAll(".tab").forEach((x) => x.setAttribute("aria-selected", x.dataset.tab === ui.tab));
    renderMain();
  }));
}

// ── main render switch ────────────────────────────────────────────────────────
function renderMain() {
  const m = el("main");
  if (ui.tab === "today") renderToday(m);
  else if (ui.tab === "browse") renderBrowse(m);
  else renderSettings(m);
  renderStats();
}

// ── TODAY (the draw) ───────────────────────────────────────────────────────────
function cardHTML(a, { actions = true } = {}) {
  const chips = [`<span class="tag cost">${esc(a.cost)}</span>`, `<span class="tag">${IOLBL[a.logistics.indoorOutdoor] || a.logistics.indoorOutdoor}</span>`];
  if (a.logistics.reservation === "required") chips.push(`<span class="tag resv">Reserve required</span>`);
  else if (a.logistics.reservation === "recommended") chips.push(`<span class="tag resv">Reserve ahead</span>`);
  if (a.season && a.season !== "Year-round") chips.push(`<span class="tag">${esc(a.season)}</span>`);
  if (a.withFriends) chips.push(`<span class="tag">Great w/ friends</span>`);
  if (a.stops && a.stops.length) chips.push(`<span class="tag">${a.stops.length}-stop crawl</span>`);
  const tag = a.nearHome ? `<span class="near-tag">near home</span>`
    : (SCOPELBL[a.scope] ? `<span class="scope-tag">${SCOPELBL[a.scope]}</span>` : "");
  const route = (a.stops && a.stops.length)
    ? `<div class="route"><p class="route-h">The route</p><ol>${a.stops.map((s) => `<li><div><div class="st-name">${esc(s.name)}</div><div class="st-note">${esc(s.note)}</div></div></li>`).join("")}</ol></div>`
    : "";
  const act = actions ? `<div class="actions">
      <button class="btn-did" data-act="done">✅ We did this</button>
      <button class="btn-skip" data-act="skip">⏭️ Skip</button></div>` : "";
  return `<div class="card anim-in" style="--catc:var(${CATVAR[a.category]})">
      <div class="card-top"><span class="cat">${esc(a.category)}</span><span class="time">${TIMELBL[a.duration]}</span></div>
      <h2>${esc(a.name)}</h2>
      <div class="hood"><span class="cdot"></span>${esc(a.neighborhood)} ${tag}</div>
      <p>${esc(a.description)}</p>
      <div class="chips">${chips.join("")}</div>${route}
    </div>${act}`;
}

function renderToday(m) {
  const now = Date.now();
  const ready = eligible(ACT, data.deck, { time: ui.time, near: ui.near }, now).length;
  let stage;
  if (ui.current && BYID[ui.current]) {
    stage = cardHTML(BYID[ui.current]);
  } else if (ui.current === "empty") {
    const soon = restingList(ACT, data.deck, now)[0];
    stage = `<div class="empty">Everything in this filter is resting.<br>Try a different amount of time, turn off <b>near home</b>, or check back later.${soon ? `<br><br>Next back: <b>${esc(soon.name)}</b> (${fmtWhen(data.deck[soon.id].until, now)}).` : ""}</div>
      <button class="draw-btn" data-draw>Try again</button>`;
  } else {
    stage = `<div class="facedown">🎴</div><button class="draw-btn" data-draw>Draw our adventure</button>
      <div class="deck-hint">${ready} card${ready === 1 ? "" : "s"} ready in this filter</div>`;
  }
  m.innerHTML = `
    <p class="brand">SF Adventures</p>
    <h1>What should we do <em>today?</em></h1>
    <p class="sub">Pick how much time you've got, then draw. Do it and it rests a while; skip it and it's back soon.</p>
    <div class="controls">
      <div class="seg" id="timeSeg">
        ${["surprise","1hr","4hr","all-day","multi-day"].map((t) =>
          `<button data-t="${t}" aria-pressed="${ui.time===t}">${t==="surprise"?"Surprise me":TIMELBL[t]}</button>`).join("")}
      </div>
      <button class="toggle" id="nearT" aria-pressed="${ui.near}"><span class="switch"></span> Near home only</button>
    </div>
    <div class="stage" id="stage">${stage}</div>`;
  el("timeSeg").querySelectorAll("button").forEach((b) => (b.onclick = () => {
    ui.time = b.dataset.t; if (ui.current && ui.current !== "empty") ui.current = null; renderToday(m);
  }));
  el("nearT").onclick = () => { ui.near = !ui.near; if (ui.current && ui.current !== "empty") ui.current = null; renderToday(m); };
  m.querySelectorAll("[data-draw]").forEach((btn) => (btn.onclick = () => doDraw(m)));
  const actWrap = m.querySelector(".actions");
  if (actWrap) actWrap.querySelectorAll("button").forEach((btn) => (btn.onclick = () => doAction(btn.dataset.act, m)));
}

function doDraw(m) {
  const a = drawOne(ACT, data.deck, { time: ui.time, near: ui.near });
  ui.current = a ? a.id : "empty";
  renderToday(m);
}

async function doAction(kind, m) {
  const a = BYID[ui.current]; if (!a) return;
  const until = cooldownUntil(kind, a.duration, CFG);
  await store.applyAction(a.id, kind, until);
  if (kind === "done") toast(`Nice — ${a.name} done! 🎉`);
  // Deal a replacement immediately. Use an optimistic deck copy so the card we
  // just acted on can't be re-drawn before the (possibly async) sync lands.
  const nextDeck = { ...data.deck, [a.id]: { until, kind } };
  const next = drawOne(ACT, nextDeck, { time: ui.time, near: ui.near });
  ui.current = next ? next.id : "empty";
  renderToday(m);
}

// ── BROWSE ─────────────────────────────────────────────────────────────────────
function renderBrowse(m) {
  m.innerHTML = `
    <div class="browse-head">
      <h1 class="browse-title">Browse</h1>
      <input class="search" id="q" type="search" placeholder="Search name, neighborhood, tag…" value="${esc(ui.q)}">
    </div>
    <div class="controls">
      <div class="seg" id="bTime">
        ${["surprise","1hr","4hr","all-day","multi-day"].map((t) =>
          `<button data-t="${t}" aria-pressed="${ui.bTime===t}">${t==="surprise"?"Any time":TIMELBL[t]}</button>`).join("")}
      </div>
      <div class="seg" id="bScope">
        ${[["all","Anywhere"],["in-city","In city"],["day-trip","Day trip"],["getaway","Getaway"]].map(([v,l]) =>
          `<button data-s="${v}" aria-pressed="${ui.bScope===v}">${l}</button>`).join("")}
      </div>
      <div class="seg" id="bCat">
        ${CATS.map((c) => `<button data-c="${esc(c)}" aria-pressed="${ui.bCat.has(c)}">${esc(c.replace(" & scenic","").replace(" & drink"," & drink"))}</button>`).join("")}
      </div>
      <button class="toggle" id="bNear" aria-pressed="${ui.bNear}"><span class="switch"></span> Near home</button>
    </div>
    <div class="count" id="bCount"></div>
    <div class="grid" id="grid"></div>`;
  el("q").oninput = (e) => { ui.q = e.target.value.trim().toLowerCase(); paintGrid(); };
  el("bTime").querySelectorAll("button").forEach((b) => (b.onclick = () => { ui.bTime = b.dataset.t; el("bTime").querySelectorAll("button").forEach((x)=>x.setAttribute("aria-pressed",x===b)); paintGrid(); }));
  el("bScope").querySelectorAll("button").forEach((b) => (b.onclick = () => { ui.bScope = b.dataset.s; el("bScope").querySelectorAll("button").forEach((x)=>x.setAttribute("aria-pressed",x===b)); paintGrid(); }));
  el("bCat").querySelectorAll("button").forEach((b) => (b.onclick = () => { const c=b.dataset.c; ui.bCat.has(c)?ui.bCat.delete(c):ui.bCat.add(c); b.setAttribute("aria-pressed", ui.bCat.has(c)); paintGrid(); }));
  el("bNear").onclick = () => { ui.bNear = !ui.bNear; el("bNear").setAttribute("aria-pressed", ui.bNear); paintGrid(); };
  paintGrid();
}

function paintGrid() {
  const now = Date.now();
  const list = ACT.filter((a) => {
    if (ui.bTime !== "surprise" && a.duration !== ui.bTime) return false;
    if (ui.bScope !== "all" && a.scope !== ui.bScope) return false;
    if (ui.bNear && !a.nearHome) return false;
    if (ui.bCat.size && !ui.bCat.has(a.category)) return false;
    if (ui.q) { const hay = (a.name + " " + a.neighborhood + " " + a.description + " " + (a.tags||[]).join(" ")).toLowerCase(); if (!hay.includes(ui.q)) return false; }
    return true;
  }).sort((x, y) => x.durationRank - y.durationRank || x.name.localeCompare(y.name));
  el("bCount").innerHTML = `Showing <b>${list.length}</b> of ${ACT.length}`;
  el("grid").innerHTML = list.map((a) => {
    const rest = isResting(data.deck, a.id, now);
    const tag = a.nearHome ? `<span class="near-tag">near home</span>` : (SCOPELBL[a.scope] ? `<span class="scope-tag">${SCOPELBL[a.scope]}</span>` : "");
    return `<article class="mini" style="--catc:var(${CATVAR[a.category]})">
      <div class="card-top"><span class="cat">${esc(a.category)}</span><span class="time">${TIMELBL[a.duration]}</span></div>
      <h3>${esc(a.name)}</h3>
      <div class="hood"><span class="cdot"></span>${esc(a.neighborhood)} ${tag}</div>
      <p>${esc(a.description)}</p>
      <div class="mini-foot">
        <span class="tag cost">${esc(a.cost)}</span>
        ${rest ? `<span class="rest-pill">Resting · ${fmtWhen(data.deck[a.id].until, now)}</span>`
               : `<button class="mini-did" data-did="${a.id}">✅ We did this</button>`}
      </div>
    </article>`;
  }).join("") || `<div class="empty">Nothing matches those filters.</div>`;
  el("grid").querySelectorAll("[data-did]").forEach((btn) => (btn.onclick = async () => {
    const a = BYID[btn.dataset.did];
    await store.applyAction(a.id, "done", cooldownUntil("done", a.duration, CFG));
    toast(`Nice — ${a.name} done! 🎉`);
  }));
}

// ── SETTINGS ───────────────────────────────────────────────────────────────────
function renderSettings(m) {
  const local = store && store.mode === "local";
  const errBox = auth.error ? `<div class="panel danger"><h3>Heads up</h3><p class="muted">${esc(auth.error)}</p><p class="muted small">Try again below. If it keeps happening, screenshot this and send it over.</p></div>` : "";
  let body;
  if (local) {
    body = `<div class="panel">
      <h3>Local mode</h3>
      <p class="muted">This device is saving its own deck. To share one live deck with Caleb, add your Firebase settings in <code>app/js/config.js</code> and redeploy — see <b>SETUP.md</b>.</p>
    </div>`;
  } else if (!auth.user) {
    body = `<div class="panel">
      <h3>Sign in</h3>
      <p class="muted">Sign in with the Google account you want on the shared deck.</p>
      <button class="primary" id="signin">Sign in with Google</button>
    </div>`;
  } else if (auth.status === "signing-in") {
    body = `<div class="panel"><p class="muted">Signing you in…</p></div>`;
  } else if (auth.household) {
    const mem = (auth.household.members || []).map((e) => `<li>${esc(e)}</li>`).join("");
    body = `<div class="panel">
      <h3>Your shared deck</h3>
      <p class="muted">Signed in as ${esc(auth.user.email)}.</p>
      <p class="label">Members</p>
      <ul class="members">${mem}</ul>
      <div class="addrow">
        <input id="memEmail" type="email" placeholder="add partner's Google email">
        <button class="primary" id="addmem">Add</button>
      </div>
      <p class="muted small">Caleb signs in with that exact Google email and the deck appears automatically.</p>
      <hr>
      <button class="ghost" id="signout">Sign out</button>
    </div>`;
  } else {
    body = `<div class="panel">
      <h3>Create your shared deck</h3>
      <p class="muted">Signed in as ${esc(auth.user.email)}. Create the deck, then add Caleb's email so it syncs to you both.</p>
      <button class="primary" id="createhh">Create our deck</button>
      <button class="ghost" id="signout">Sign out</button>
    </div>`;
  }
  m.innerHTML = `<h1 class="browse-title">Settings</h1>${errBox}${body}
    <div class="panel danger">
      <h3>Reset the deck</h3>
      <p class="muted">Clears all cooldowns and history${local ? " on this device" : " for everyone on the deck"}.</p>
      <button class="ghost warn" id="reset">Reset deck</button>
    </div>`;
  const on = (id, fn) => { const e = el(id); if (e) e.onclick = fn; };
  on("signin", async () => { try { await store.signIn(); } catch (e) { alert("Sign-in failed: " + e.message); } });
  on("signout", async () => { await store.signOut(); });
  on("createhh", async () => { try { await store.createHousehold(); } catch (e) { alert(e.message); } });
  on("addmem", async () => {
    const v = el("memEmail").value.trim().toLowerCase();
    if (!v || !v.includes("@")) return alert("Enter a valid email.");
    try { await store.addMember(v); el("memEmail").value = ""; toast("Added " + v); } catch (e) { alert(e.message); }
  });
  on("reset", async () => { if (confirm("Reset the whole deck? Clears cooldowns + history.")) await store.reset(); });
}

// ── stats bar (shared across tabs) ─────────────────────────────────────────────
function renderStats() {
  const s = el("stats"); if (!s) return;
  const now = Date.now();
  const rest = restingList(ACT, data.deck, now);
  const ready = ACT.length - rest.length;
  s.innerHTML = `<span><b>${ready}</b> ready</span><span><b>${rest.length}</b> resting</span><span><b>${data.log.length}</b> done</span>`
    + (rest.length ? `<details class="rest-details"><summary>Resting (${rest.length})</summary><div class="shelf">${
        rest.map((a) => `<div class="shelf-row ${data.deck[a.id].kind==='done'?'rest-done':''}"><span>${esc(a.name)}</span><span class="rt">${data.deck[a.id].kind==='done'?'✓ ':''}${fmtWhen(data.deck[a.id].until, now)}</span></div>`).join("")
      }</div></details>` : "");
}

// ── toast ───────────────────────────────────────────────────────────────────────
let toastT;
function toast(msg) {
  const t = el("toast"); if (!t) return;
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2200);
}

// register service worker for installability
if ("serviceWorker" in navigator) navigator.serviceWorker.register("./sw.js").catch(() => {});
