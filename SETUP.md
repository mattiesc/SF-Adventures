# Setting up SF Adventures (Firebase)

The app **already runs** without any of this — open `app/index.html` (or deploy it) and it works in **local mode** (each phone keeps its own deck). Do the steps below when you want the **shared, synced deck** for you + Caleb.

Everything here is free. No credit card. Total time ~15 minutes.

---

## 1. Create a Firebase project (~3 min)

1. Go to <https://console.firebase.google.com> and sign in with your Google account.
2. Click **Add project** → name it (e.g. `sf-adventures`) → you can turn Google Analytics **off** → **Create project**.

## 2. Turn on Google sign-in (~2 min)

1. In the left menu: **Build → Authentication → Get started**.
2. Under **Sign-in method**, click **Google → Enable**, pick a support email, **Save**.

## 3. Create the database (~2 min)

1. Left menu: **Build → Firestore Database → Create database**.
2. Choose a location near you (e.g. `us-west`), start in **production mode**, **Enable**.

## 4. Register the web app & copy the config (~3 min)

1. Click the ⚙️ gear (top-left) → **Project settings**.
2. Scroll to **Your apps** → click the **`</>`** (web) icon → give it a nickname → **Register app**.
3. You'll see a `firebaseConfig = { ... }` snippet. Copy the values.
4. Open **`app/js/config.js`** in this repo and paste them in (apiKey, authDomain, projectId, appId).

## 5. Install the tools & deploy (~5 min)

You need [Node.js](https://nodejs.org) installed. Then, from this repo folder:

```bash
npm install -g firebase-tools     # one time
firebase login                    # opens a browser; sign in with the same Google account
```

Put your project id into **`.firebaserc`** (replace `PASTE_YOUR_FIREBASE_PROJECT_ID`), then:

```bash
firebase deploy --only firestore:rules   # publishes the security rules
firebase deploy --only hosting           # publishes the app
```

Firebase prints a URL like `https://sf-adventures-xxxx.web.app`. That's your app.

## 6. First run — create your shared deck

1. Open the URL on your phone. **Add to Home Screen** (Share → Add to Home Screen on iPhone; menu → Install on Android).
2. Go to **Settings → Sign in with Google**.
3. Tap **Create our deck**, then add **Caleb's Google email** under Members.
4. Caleb opens the same URL, signs in with that email → the shared deck appears. Draw away. 🎴

---

## Updating the content later

The adventure list lives in `data/activities.json`. After editing it:

```bash
cp data/activities.json app/activities.json   # ship the new list with the app
firebase deploy --only hosting
```

## Notes

- The values in `app/js/config.js` are **not secrets** — they're safe to commit. Access is controlled by the Firestore rules (only your two emails).
- Free-tier Firebase Hosting does **not** auto-pause, so the app is always ready.
- To keep costs impossible: don't upgrade to the paid **Blaze** plan. The free **Spark** plan cannot bill you.
