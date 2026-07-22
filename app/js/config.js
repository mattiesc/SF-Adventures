// ─────────────────────────────────────────────────────────────────────────────
//  Firebase configuration.  See SETUP.md for a click-by-click guide.
//
//  These values are NOT secret — they're meant to ship in client code. Your data
//  is protected by Firestore security rules + the two allowed emails, not by
//  hiding these. Until you paste real values here, the app runs in LOCAL mode
//  (saves on this device only, no sharing).
// ─────────────────────────────────────────────────────────────────────────────

export const firebaseConfig = {
  apiKey: "PASTE_ME",
  authDomain: "PASTE_ME",        // e.g. sf-adventures-xxxx.firebaseapp.com
  projectId: "PASTE_ME",         // e.g. sf-adventures-xxxx
  appId: "PASTE_ME",
  // These two are optional for this app but Firebase usually gives them to you:
  storageBucket: "",
  messagingSenderId: "",
};

// True when the config above still has placeholders → run in local-only mode.
export const isLocalMode = Object.values(firebaseConfig).some(
  (v) => typeof v === "string" && v.includes("PASTE_ME")
);
