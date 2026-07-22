// Pure cooldown-deck logic. No DOM, no Firebase — easy to reason about and reuse.

export const DAY = 86400000;

// Fallback cooldowns (days). The real values come from activities.json -> meta.deck,
// but we keep a copy here so the module works even if meta is missing.
export const DEFAULT_COOLDOWNS = {
  doCooldownDays:   { "1hr": 14, "4hr": 30, "all-day": 91, "multi-day": 365 },
  skipCooldownDays: { "1hr": 3,  "4hr": 7,  "all-day": 14, "multi-day": 30 },
};

// deckState shape: { [activityId]: { until: <epoch ms>, kind: "done"|"skip", by?: email, at?: ms } }

export function isResting(deckState, id, now = Date.now()) {
  const s = deckState[id];
  return !!(s && s.until > now);
}

// Compute the epoch ms when a card should return to the pool.
export function cooldownUntil(kind, duration, cfg = DEFAULT_COOLDOWNS, now = Date.now()) {
  const table = kind === "done" ? cfg.doCooldownDays : cfg.skipCooldownDays;
  const days = table[duration] ?? table["4hr"];
  return now + days * DAY;
}

// Eligible pool given filters. `time` is a duration tier or "surprise". `near` restricts to nearHome.
export function eligible(activities, deckState, { time = "surprise", near = false } = {}, now = Date.now()) {
  return activities.filter((a) => {
    if (isResting(deckState, a.id, now)) return false;
    if (near && !a.nearHome) return false;
    if (time !== "surprise" && a.duration !== time) return false;
    return true;
  });
}

// Draw one random activity from the eligible pool. Returns the activity or null.
// `rng` injectable for deterministic tests.
export function drawOne(activities, deckState, filters, now = Date.now(), rng = Math.random) {
  const pool = eligible(activities, deckState, filters, now);
  if (!pool.length) return null;
  return pool[Math.floor(rng() * pool.length)];
}

export function restingList(activities, deckState, now = Date.now()) {
  return activities
    .filter((a) => isResting(deckState, a.id, now))
    .sort((x, y) => deckState[x.id].until - deckState[y.id].until);
}

// Human label for when a resting card returns.
export function fmtWhen(untilMs, now = Date.now()) {
  const days = Math.max(1, Math.round((untilMs - now) / DAY));
  if (days < 14) return `back in ${days}d`;
  if (days < 60) return `back in ${Math.round(days / 7)}w`;
  if (days < 400) return `back in ${Math.round(days / 30)}mo`;
  return "back in ~1yr";
}
