// ─────────────────────────────────────────────────────────────────────────────
//  Firebase configuration.  See SETUP.md for a click-by-click guide.
//
//  These values are NOT secret — they're meant to ship in client code. Your data
//  is protected by Firestore security rules + the two allowed emails, not by
//  hiding these. Until you paste real values here, the app runs in LOCAL mode
//  (saves on this device only, no sharing).
// ─────────────────────────────────────────────────────────────────────────────

export const firebaseConfig = {
  apiKey: "AIzaSyA06rCCHAHWfWToowKrFVMtD8D2mEYko24",
  authDomain: "sf-adventures-eb199.firebaseapp.com",
  projectId: "sf-adventures-eb199",
  appId: "1:810201582362:web:9fbcdfd089631bdeb77aa3",
  storageBucket: "sf-adventures-eb199.firebasestorage.app",
  messagingSenderId: "810201582362",
};

// True when the config above still has placeholders → run in local-only mode.
export const isLocalMode = Object.values(firebaseConfig).some(
  (v) => typeof v === "string" && v.includes("PASTE_ME")
);
