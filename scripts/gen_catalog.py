# -*- coding: utf-8 -*-
import json

data = json.load(open("data/activities.json"))
acts = data["activities"]

# nearHome is authored in the JSON now; fall back to a keyword guess only if missing.
NEAR = ("Pacific Heights", "Polk Gulch", "Nob Hill", "Russian Hill",
        "Van Ness", "Japantown", "Fillmore", "Marina", "Cow Hollow")
for a in acts:
    if "nearHome" not in a:
        a["nearHome"] = any(k in a["neighborhood"] for k in NEAR)

payload = json.dumps(acts, ensure_ascii=False)

html = r"""<title>SF Adventures — Catalog</title>
<style>
  :root {
    --bg: #ECEEEC; --surface: #FBFCFA; --surface-2: #F1F3EF;
    --ink: #23282C; --ink-soft: #5A6169; --ink-faint: #8A9199;
    --line: #DBDDD8; --line-strong: #C7CAC3;
    --accent: #1F6E93; --accent-ink: #FFFFFF; --accent-soft: #E4EEF3;
    --cat-out: #2F8F6B; --cat-food: #CC6A2C; --cat-arts: #7156B0; --cat-play: #C74E86;
    --warn: #B26A15;
    --shadow: 0 1px 2px rgba(30,40,50,.04), 0 6px 18px rgba(30,40,50,.06);
    --radius: 14px;
    --font-display: "Hoefler Text","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --font-sans: system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --font-mono: ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #14171B; --surface: #1D2128; --surface-2: #232932;
      --ink: #E8E8E2; --ink-soft: #A2AAB3; --ink-faint: #79828C;
      --line: #2C323B; --line-strong: #3A414B;
      --accent: #58A9D0; --accent-ink: #0B0F13; --accent-soft: #1B2C36;
      --cat-out: #48B189; --cat-food: #E28A4C; --cat-arts: #9A88D2; --cat-play: #E070A0;
      --warn: #D89A46;
      --shadow: 0 1px 2px rgba(0,0,0,.25), 0 8px 22px rgba(0,0,0,.28);
    }
  }
  :root[data-theme="light"] {
    --bg: #ECEEEC; --surface: #FBFCFA; --surface-2: #F1F3EF;
    --ink: #23282C; --ink-soft: #5A6169; --ink-faint: #8A9199;
    --line: #DBDDD8; --line-strong: #C7CAC3;
    --accent: #1F6E93; --accent-ink: #FFFFFF; --accent-soft: #E4EEF3;
    --cat-out: #2F8F6B; --cat-food: #CC6A2C; --cat-arts: #7156B0; --cat-play: #C74E86;
    --warn: #B26A15; --shadow: 0 1px 2px rgba(30,40,50,.04), 0 6px 18px rgba(30,40,50,.06);
  }
  :root[data-theme="dark"] {
    --bg: #14171B; --surface: #1D2128; --surface-2: #232932;
    --ink: #E8E8E2; --ink-soft: #A2AAB3; --ink-faint: #79828C;
    --line: #2C323B; --line-strong: #3A414B;
    --accent: #58A9D0; --accent-ink: #0B0F13; --accent-soft: #1B2C36;
    --cat-out: #48B189; --cat-food: #E28A4C; --cat-arts: #9A88D2; --cat-play: #E070A0;
    --warn: #D89A46; --shadow: 0 1px 2px rgba(0,0,0,.25), 0 8px 22px rgba(0,0,0,.28);
  }

  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink);
    font-family: var(--font-sans); line-height: 1.55;
    -webkit-font-smoothing: antialiased; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 0 20px 80px; }

  /* Hero */
  header.hero { padding: 46px 0 26px; }
  .eyebrow { font-family: var(--font-mono); font-size: .72rem; letter-spacing: .16em;
    text-transform: uppercase; color: var(--accent); margin: 0 0 10px; }
  h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.5rem, 6vw, 4rem);
    line-height: 1.02; letter-spacing: -.01em; margin: 0; text-wrap: balance; }
  h1 em { font-style: italic; color: var(--accent); }
  .lede { max-width: 60ch; color: var(--ink-soft); font-size: 1.05rem; margin: 16px 0 0; }

  /* Controls */
  .controls { position: sticky; top: 0; z-index: 20; margin-top: 26px;
    background: color-mix(in srgb, var(--bg) 88%, transparent);
    backdrop-filter: blur(10px);
    border: 1px solid var(--line); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 14px 16px; display: flex;
    flex-wrap: wrap; gap: 16px 22px; align-items: center; }
  .group { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .group > .lbl { font-family: var(--font-mono); font-size: .68rem; letter-spacing: .12em;
    text-transform: uppercase; color: var(--ink-faint); margin-right: 2px; }
  .chip { font: 500 .82rem/1 var(--font-sans); color: var(--ink-soft);
    background: var(--surface-2); border: 1px solid var(--line);
    padding: 7px 12px; border-radius: 999px; cursor: pointer;
    transition: all .14s ease; white-space: nowrap; }
  .chip:hover { border-color: var(--line-strong); color: var(--ink); }
  .chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent);
    color: var(--accent-ink); }
  .chip.cat[aria-pressed="true"] { background: var(--catc); border-color: var(--catc); color: #fff; }
  .chip:focus-visible, .toggle:focus-visible, .search:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .search { flex: 1 1 180px; min-width: 150px; font-size: .9rem; color: var(--ink);
    background: var(--surface); border: 1px solid var(--line); border-radius: 999px;
    padding: 8px 14px; font-family: var(--font-sans); }
  .search::placeholder { color: var(--ink-faint); }
  .toggle { display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
    font-size: .82rem; color: var(--ink-soft); background: none; border: 0; padding: 0; }
  .switch { width: 38px; height: 22px; border-radius: 999px; background: var(--line-strong);
    position: relative; transition: background .16s ease; flex: none; }
  .switch::after { content: ""; position: absolute; top: 2px; left: 2px; width: 18px; height: 18px;
    border-radius: 50%; background: #fff; transition: transform .16s ease; box-shadow: 0 1px 2px rgba(0,0,0,.3); }
  .toggle[aria-pressed="true"] .switch { background: var(--cat-food); }
  .toggle[aria-pressed="true"] .switch::after { transform: translateX(16px); }

  .meta-row { display: flex; align-items: baseline; justify-content: space-between;
    gap: 12px; margin: 22px 2px 14px; flex-wrap: wrap; }
  .count { font-family: var(--font-mono); font-size: .82rem; color: var(--ink-soft); }
  .count b { color: var(--ink); }
  .reset { font-family: var(--font-mono); font-size: .74rem; letter-spacing: .04em;
    color: var(--accent); background: none; border: 0; cursor: pointer; }
  .reset:hover { text-decoration: underline; }

  /* Grid */
  .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(288px, 1fr));
    align-items: start; }
  .card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 18px 18px 16px; display: flex; flex-direction: column;
    gap: 10px; position: relative; overflow: hidden; }
  .card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: var(--catc); }
  .card-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  .cat-label { font-family: var(--font-mono); font-size: .66rem; letter-spacing: .1em;
    text-transform: uppercase; color: var(--catc); font-weight: 600; }
  .time { font-family: var(--font-mono); font-size: .74rem; color: var(--ink-soft);
    background: var(--surface-2); border: 1px solid var(--line); padding: 3px 9px;
    border-radius: 999px; white-space: nowrap; font-variant-numeric: tabular-nums; }
  h3 { font-family: var(--font-display); font-weight: 600; font-size: 1.24rem; line-height: 1.15;
    margin: 0; letter-spacing: -.005em; text-wrap: balance; }
  .hood { font-size: .8rem; color: var(--ink-faint); display: flex; align-items: center; gap: 6px; margin-top: -3px; }
  .hood .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--catc); flex: none; }
  .near-tag { font-family: var(--font-mono); font-size: .6rem; letter-spacing: .08em; text-transform: uppercase;
    color: var(--cat-food); border: 1px solid color-mix(in srgb, var(--cat-food) 40%, var(--line));
    border-radius: 4px; padding: 1px 5px; margin-left: 2px; }
  .scope-tag { font-family: var(--font-mono); font-size: .6rem; letter-spacing: .08em; text-transform: uppercase;
    color: var(--accent); border: 1px solid color-mix(in srgb, var(--accent) 40%, var(--line));
    border-radius: 4px; padding: 1px 5px; margin-left: 2px; }
  .tag.season { color: var(--cat-out); border-color: color-mix(in srgb, var(--cat-out) 35%, var(--line)); }
  .tag.friends { color: var(--cat-arts); border-color: color-mix(in srgb, var(--cat-arts) 35%, var(--line)); }
  .desc { font-size: .9rem; color: var(--ink-soft); margin: 2px 0 0; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; padding-top: 6px; }
  .tag { font-family: var(--font-mono); font-size: .68rem; color: var(--ink-soft);
    background: var(--surface-2); border: 1px solid var(--line); padding: 3px 8px; border-radius: 6px;
    font-variant-numeric: tabular-nums; }
  .tag.cost { color: var(--ink); font-weight: 600; }
  .tag.resv { color: var(--warn); border-color: color-mix(in srgb, var(--warn) 35%, var(--line)); }
  .tag.dog::before { content: "\1F43E  "; }
  .pairs { font-size: .76rem; color: var(--ink-faint); border-top: 1px dashed var(--line);
    padding-top: 9px; margin-top: 4px; }
  .crawl-badge { font-family: var(--font-mono); font-size: .6rem; letter-spacing: .09em;
    text-transform: uppercase; color: var(--catc); border: 1px solid var(--catc);
    border-radius: 4px; padding: 2px 6px; font-weight: 600; }
  .route { border-top: 1px dashed var(--line); padding-top: 10px; margin-top: 2px; }
  .route-h { font-family: var(--font-mono); font-size: .64rem; letter-spacing: .08em;
    text-transform: uppercase; color: var(--ink-faint); margin: 0 0 8px; }
  .route ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 9px;
    counter-reset: stop; }
  .route li { display: grid; grid-template-columns: 22px 1fr; gap: 9px; align-items: start; }
  .route li::before { counter-increment: stop; content: counter(stop);
    font-family: var(--font-mono); font-size: .72rem; font-weight: 600; color: var(--catc);
    width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
    background: color-mix(in srgb, var(--catc) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--catc) 35%, transparent); }
  .route .st-name { font-size: .84rem; font-weight: 600; color: var(--ink); }
  .route .st-note { font-size: .8rem; color: var(--ink-soft); }
  .pairs b { color: var(--ink-soft); font-weight: 600; font-family: var(--font-mono);
    font-size: .64rem; letter-spacing: .08em; text-transform: uppercase; }
  .empty { text-align: center; color: var(--ink-soft); padding: 60px 20px; font-size: .95rem; }
  footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line);
    color: var(--ink-faint); font-size: .78rem; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header class="hero">
    <p class="eyebrow">San Francisco · adventures for two</p>
    <h1>SF <em>Adventures</em></h1>
    <p class="lede">A working catalog of things to do — from a one-hour break near home to a full-on weekend getaway — filtered the way a busy weekend actually works: by how much time you've got, what it costs, and how far you're willing to roam.</p>
  </header>

  <div class="controls" id="controls">
    <div class="group" data-filter="time">
      <span class="lbl">Time</span>
      <button class="chip" data-val="all" aria-pressed="true">Any</button>
      <button class="chip" data-val="1hr" aria-pressed="false">~1 hr</button>
      <button class="chip" data-val="4hr" aria-pressed="false">~4 hrs</button>
      <button class="chip" data-val="all-day" aria-pressed="false">All day</button>
      <button class="chip" data-val="multi-day" aria-pressed="false">Multi-day</button>
    </div>
    <div class="group" data-filter="scope">
      <span class="lbl">Where</span>
      <button class="chip" data-val="all" aria-pressed="true">Any</button>
      <button class="chip" data-val="in-city" aria-pressed="false">In the city</button>
      <button class="chip" data-val="day-trip" aria-pressed="false">Day trip</button>
      <button class="chip" data-val="getaway" aria-pressed="false">Getaway</button>
    </div>
    <div class="group" data-filter="cost">
      <span class="lbl">Cost</span>
      <button class="chip" data-val="all" aria-pressed="true">Any</button>
      <button class="chip" data-val="0" aria-pressed="false">Free</button>
      <button class="chip" data-val="1" aria-pressed="false">$</button>
      <button class="chip" data-val="2" aria-pressed="false">$$</button>
      <button class="chip" data-val="3" aria-pressed="false">$$$</button>
    </div>
    <div class="group" data-filter="cat" id="catGroup">
      <span class="lbl">Type</span>
    </div>
    <button class="toggle" id="nearToggle" aria-pressed="false">
      <span class="switch"></span> Near home
    </button>
    <button class="toggle" id="crawlToggle" aria-pressed="false">
      <span class="switch"></span> Crawls only
    </button>
    <input class="search" id="search" type="search" placeholder="Search name, neighborhood, tag…" aria-label="Search adventures">
  </div>

  <div class="meta-row">
    <div class="count" id="count"></div>
    <button class="reset" id="reset">Clear filters</button>
  </div>

  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" hidden>No adventures match those filters. Try loosening one.</div>

  <footer>
    Generated from <code>data/activities.json</code> — the app's source of truth. Hours, prices &amp; reservations drift; verify before you go.
  </footer>
</div>

<script>
const ACTS = __PAYLOAD__;
const CATS = ["Outdoorsy & scenic","Food & drink","Arts & culture","Playful & active"];
const CATVAR = {"Outdoorsy & scenic":"--cat-out","Food & drink":"--cat-food","Arts & culture":"--cat-arts","Playful & active":"--cat-play"};
const TIMELBL = {"1hr":"~1 hr","4hr":"~4 hrs","all-day":"All day"};
const IOLBL = {"indoor":"Indoor","outdoor":"Outdoor","mixed":"Indoor + out"};
const nameById = Object.fromEntries(ACTS.map(a => [a.id, a.name]));

const state = { time:"all", cost:"all", scope:"all", cats:new Set(), near:false, crawl:false, q:"" };
const SCOPELBL = {"day-trip":"Day trip","getaway":"Getaway"};

// Build category chips
const catGroup = document.getElementById("catGroup");
CATS.forEach(c => {
  const b = document.createElement("button");
  b.className = "chip cat"; b.textContent = c.replace(" & ", " & ");
  b.dataset.val = c; b.setAttribute("aria-pressed","false");
  b.style.setProperty("--catc", `var(${CATVAR[c]})`);
  b.addEventListener("click", () => {
    if (state.cats.has(c)) state.cats.delete(c); else state.cats.add(c);
    b.setAttribute("aria-pressed", state.cats.has(c));
    render();
  });
  catGroup.appendChild(b);
});

// Segmented groups (time, cost)
document.querySelectorAll('.group[data-filter]').forEach(g => {
  const key = g.dataset.filter;
  if (key === "cat") return;
  g.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      state[key] = chip.dataset.val;
      g.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", c === chip));
      render();
    });
  });
});

const nearBtn = document.getElementById("nearToggle");
nearBtn.addEventListener("click", () => {
  state.near = !state.near;
  nearBtn.setAttribute("aria-pressed", state.near);
  render();
});
const crawlBtn = document.getElementById("crawlToggle");
crawlBtn.addEventListener("click", () => {
  state.crawl = !state.crawl;
  crawlBtn.setAttribute("aria-pressed", state.crawl);
  render();
});
document.getElementById("search").addEventListener("input", e => {
  state.q = e.target.value.trim().toLowerCase(); render();
});
document.getElementById("reset").addEventListener("click", () => {
  state.time="all"; state.cost="all"; state.scope="all"; state.cats.clear(); state.near=false; state.crawl=false; state.q="";
  document.getElementById("search").value = "";
  document.querySelectorAll('.group[data-filter="time"] .chip, .group[data-filter="cost"] .chip, .group[data-filter="scope"] .chip')
    .forEach(c => c.setAttribute("aria-pressed", c.dataset.val === "all"));
  document.querySelectorAll(".chip.cat").forEach(c => c.setAttribute("aria-pressed","false"));
  nearBtn.setAttribute("aria-pressed","false");
  crawlBtn.setAttribute("aria-pressed","false");
  render();
});

function matches(a) {
  if (state.time !== "all" && a.duration !== state.time) return false;
  if (state.cost !== "all" && String(a.costLevel) !== state.cost) return false;
  if (state.scope !== "all" && a.scope !== state.scope) return false;
  if (state.cats.size && !state.cats.has(a.category)) return false;
  if (state.near && !a.nearHome) return false;
  if (state.crawl && !(a.stops && a.stops.length)) return false;
  if (state.q) {
    const hay = (a.name + " " + a.neighborhood + " " + a.description + " " + (a.tags||[]).join(" ")).toLowerCase();
    if (!hay.includes(state.q)) return false;
  }
  return true;
}

function card(a) {
  const L = a.logistics || {};
  const chips = [];
  chips.push(`<span class="tag cost">${a.cost}</span>`);
  chips.push(`<span class="tag">${IOLBL[L.indoorOutdoor]||L.indoorOutdoor}</span>`);
  if (L.reservation === "required") chips.push(`<span class="tag resv">Reserve required</span>`);
  else if (L.reservation === "recommended") chips.push(`<span class="tag resv">Reserve ahead</span>`);
  if (L.dogFriendly) chips.push(`<span class="tag dog">Dogs OK</span>`);
  if (a.season && a.season !== "Year-round") chips.push(`<span class="tag season">${a.season}</span>`);
  if (a.withFriends) chips.push(`<span class="tag friends">Great w/ friends</span>`);
  const pairs = (a.pairsWith||[]).map(id => nameById[id]).filter(Boolean);
  const pairsHtml = pairs.length ? `<div class="pairs"><b>Pairs with</b> ${pairs.join(" · ")}</div>` : "";
  const near = a.nearHome ? `<span class="near-tag">near home</span>`
             : (SCOPELBL[a.scope] ? `<span class="scope-tag">${SCOPELBL[a.scope]}</span>` : "");
  const isCrawl = a.stops && a.stops.length;
  const topRight = isCrawl
    ? `<span class="crawl-badge">${a.stops.length}-stop crawl</span>`
    : `<span class="time">${TIMELBL[a.duration]||a.duration}</span>`;
  let routeHtml = "";
  if (isCrawl) {
    const items = a.stops.map(s =>
      `<li><div><div class="st-name">${s.name}</div><div class="st-note">${s.note}</div></div></li>`).join("");
    routeHtml = `<div class="route"><p class="route-h">The route · ${TIMELBL[a.duration]||a.duration}</p><ol>${items}</ol></div>`;
  }
  return `<article class="card" style="--catc:var(${CATVAR[a.category]})">
    <div class="card-top">
      <span class="cat-label">${a.category}</span>
      ${topRight}
    </div>
    <h3>${a.name}</h3>
    <div class="hood"><span class="dot"></span>${a.neighborhood}${near}</div>
    <p class="desc">${a.description}</p>
    <div class="chips">${chips.join("")}</div>
    ${routeHtml}
    ${pairsHtml}
  </article>`;
}

function render() {
  const list = ACTS.filter(matches).sort((x,y) => x.durationRank - y.durationRank || x.name.localeCompare(y.name));
  const grid = document.getElementById("grid");
  grid.innerHTML = list.map(card).join("");
  document.getElementById("empty").hidden = list.length > 0;
  document.getElementById("count").innerHTML = `Showing <b>${list.length}</b> of ${ACTS.length} adventures`;
}
render();
</script>
"""

html = html.replace("__PAYLOAD__", payload)
out = "preview/catalog.html"
open(out, "w").write(html)
print("wrote", out, len(html), "bytes;", len(acts), "activities")
