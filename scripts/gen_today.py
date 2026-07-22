# -*- coding: utf-8 -*-
import json
d = json.load(open("data/activities.json"))
deck = d["meta"]["deck"]
slim = []
for a in d["activities"]:
    L = a["logistics"]
    slim.append({
        "id": a["id"], "name": a["name"], "category": a["category"],
        "neighborhood": a["neighborhood"], "duration": a["duration"],
        "cost": a["cost"], "nearHome": a["nearHome"], "scope": a["scope"],
        "description": a["description"], "season": a.get("season", "Year-round"),
        "withFriends": a.get("withFriends", False), "reservation": L["reservation"],
        "io": L["indoorOutdoor"], "dog": L["dogFriendly"],
        "stops": len(a.get("stops", []) or [])
    })
payload = json.dumps(slim, ensure_ascii=False)
cfg = json.dumps(deck, ensure_ascii=False)

html = r"""<title>SF Adventures — Today</title>
<style>
  :root {
    --bg:#ECEEEC; --surface:#FBFCFA; --surface-2:#F1F3EF; --ink:#23282C; --ink-soft:#5A6169;
    --ink-faint:#8A9199; --line:#DBDDD8; --line-strong:#C7CAC3; --accent:#1F6E93; --accent-ink:#FFF;
    --good:#2F8F6B; --good-ink:#fff; --warn:#B26A15;
    --cat-out:#2F8F6B; --cat-food:#CC6A2C; --cat-arts:#7156B0; --cat-play:#C74E86;
    --shadow:0 1px 2px rgba(30,40,50,.05),0 10px 30px rgba(30,40,50,.09);
    --radius:16px;
    --font-display:"Hoefler Text","Palatino Linotype",Palatino,Georgia,serif;
    --font-sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --font-mono:ui-monospace,"SF Mono","Cascadia Code",Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme:dark){:root{
    --bg:#14171B; --surface:#1D2128; --surface-2:#232932; --ink:#E8E8E2; --ink-soft:#A2AAB3;
    --ink-faint:#79828C; --line:#2C323B; --line-strong:#3A414B; --accent:#58A9D0; --accent-ink:#0B0F13;
    --good:#48B189; --warn:#D89A46;
    --cat-out:#48B189; --cat-food:#E28A4C; --cat-arts:#9A88D2; --cat-play:#E070A0;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 34px rgba(0,0,0,.4);
  }}
  :root[data-theme="light"]{--bg:#ECEEEC;--surface:#FBFCFA;--surface-2:#F1F3EF;--ink:#23282C;--ink-soft:#5A6169;--ink-faint:#8A9199;--line:#DBDDD8;--line-strong:#C7CAC3;--accent:#1F6E93;--accent-ink:#FFF;--good:#2F8F6B;--warn:#B26A15;--cat-out:#2F8F6B;--cat-food:#CC6A2C;--cat-arts:#7156B0;--cat-play:#C74E86;--shadow:0 1px 2px rgba(30,40,50,.05),0 10px 30px rgba(30,40,50,.09);}
  :root[data-theme="dark"]{--bg:#14171B;--surface:#1D2128;--surface-2:#232932;--ink:#E8E8E2;--ink-soft:#A2AAB3;--ink-faint:#79828C;--line:#2C323B;--line-strong:#3A414B;--accent:#58A9D0;--accent-ink:#0B0F13;--good:#48B189;--warn:#D89A46;--cat-out:#48B189;--cat-food:#E28A4C;--cat-arts:#9A88D2;--cat-play:#E070A0;--shadow:0 1px 2px rgba(0,0,0,.3),0 12px 34px rgba(0,0,0,.4);}
  *{box-sizing:border-box;}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-sans);line-height:1.5;-webkit-font-smoothing:antialiased;}
  .wrap{max-width:560px;margin:0 auto;padding:34px 20px 70px;}
  .brand{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);text-align:center;margin-bottom:8px;}
  h1{font-family:var(--font-display);font-weight:600;font-size:clamp(2rem,7vw,2.9rem);line-height:1.05;text-align:center;margin:0 0 6px;text-wrap:balance;}
  h1 em{font-style:italic;color:var(--accent);}
  .sub{text-align:center;color:var(--ink-soft);font-size:.98rem;margin:0 auto 22px;max-width:44ch;}

  .controls{display:flex;flex-direction:column;gap:12px;align-items:center;margin-bottom:22px;}
  .seg{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:5px;}
  .seg button{font:500 .82rem/1 var(--font-sans);color:var(--ink-soft);background:transparent;border:0;padding:8px 13px;border-radius:999px;cursor:pointer;transition:all .14s;white-space:nowrap;}
  .seg button:hover{color:var(--ink);}
  .seg button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);}
  .toggle{display:inline-flex;align-items:center;gap:8px;cursor:pointer;font-size:.85rem;color:var(--ink-soft);background:none;border:0;}
  .switch{width:38px;height:22px;border-radius:999px;background:var(--line-strong);position:relative;transition:background .16s;}
  .switch::after{content:"";position:absolute;top:2px;left:2px;width:18px;height:18px;border-radius:50%;background:#fff;transition:transform .16s;box-shadow:0 1px 2px rgba(0,0,0,.3);}
  .toggle[aria-pressed="true"] .switch{background:var(--cat-food);}
  .toggle[aria-pressed="true"] .switch::after{transform:translateX(16px);}

  .stage{min-height:340px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
  .draw-btn{font:600 1.02rem/1 var(--font-sans);color:var(--accent-ink);background:var(--accent);border:0;border-radius:999px;padding:16px 30px;cursor:pointer;box-shadow:var(--shadow);transition:transform .12s,filter .12s;}
  .draw-btn:hover{filter:brightness(1.06);}
  .draw-btn:active{transform:scale(.97);}
  .deck-hint{margin-top:14px;font-family:var(--font-mono);font-size:.74rem;color:var(--ink-faint);}
  .facedown{width:150px;height:150px;border-radius:var(--radius);margin-bottom:22px;
    background:repeating-linear-gradient(45deg,var(--surface-2),var(--surface-2) 10px,var(--surface) 10px,var(--surface) 20px);
    border:1px solid var(--line);display:grid;place-items:center;color:var(--ink-faint);font-size:2rem;box-shadow:var(--shadow);}

  .card{width:100%;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:22px 22px 20px;position:relative;overflow:hidden;--catc:var(--accent);}
  .card::before{content:"";position:absolute;inset:0 auto 0 0;width:5px;background:var(--catc);}
  .card-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px;}
  .cat{font-family:var(--font-mono);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:var(--catc);font-weight:600;}
  .time{font-family:var(--font-mono);font-size:.74rem;color:var(--ink-soft);background:var(--surface-2);border:1px solid var(--line);padding:3px 9px;border-radius:999px;}
  .card h2{font-family:var(--font-display);font-weight:600;font-size:1.6rem;line-height:1.12;margin:0 0 4px;text-wrap:balance;}
  .hood{font-size:.85rem;color:var(--ink-faint);display:flex;align-items:center;gap:6px;flex-wrap:wrap;}
  .hood .dot{width:7px;height:7px;border-radius:50%;background:var(--catc);}
  .near-tag,.scope-tag{font-family:var(--font-mono);font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;border-radius:4px;padding:1px 5px;}
  .near-tag{color:var(--cat-food);border:1px solid color-mix(in srgb,var(--cat-food) 40%,var(--line));}
  .scope-tag{color:var(--accent);border:1px solid color-mix(in srgb,var(--accent) 40%,var(--line));}
  .card p{font-size:.94rem;color:var(--ink-soft);margin:12px 0 0;}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px;}
  .tag{font-family:var(--font-mono);font-size:.68rem;color:var(--ink-soft);background:var(--surface-2);border:1px solid var(--line);padding:3px 8px;border-radius:6px;}
  .tag.cost{color:var(--ink);font-weight:600;}
  .tag.resv{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,var(--line));}

  .actions{display:flex;gap:10px;margin-top:18px;width:100%;}
  .actions button{flex:1;font:600 .95rem/1 var(--font-sans);padding:14px;border-radius:12px;cursor:pointer;border:1px solid var(--line);transition:transform .12s,filter .12s;}
  .actions button:active{transform:scale(.97);}
  .btn-did{background:var(--good);color:#fff;border-color:var(--good);}
  .btn-did:hover{filter:brightness(1.06);}
  .btn-skip{background:var(--surface);color:var(--ink-soft);}
  .btn-skip:hover{color:var(--ink);border-color:var(--line-strong);}

  .anim-in{animation:deal .42s cubic-bezier(.2,.8,.2,1);}
  @keyframes deal{from{opacity:0;transform:translateY(26px) rotate(-3deg) scale(.94);}to{opacity:1;transform:none;}}
  .toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);background:var(--good);color:#fff;font-weight:600;font-size:.9rem;padding:11px 20px;border-radius:999px;box-shadow:var(--shadow);opacity:0;pointer-events:none;transition:all .3s;z-index:50;}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0);}

  .stats{display:flex;justify-content:center;gap:20px;margin-top:26px;font-family:var(--font-mono);font-size:.76rem;color:var(--ink-soft);}
  .stats b{color:var(--ink);font-variant-numeric:tabular-nums;}
  .empty{text-align:center;color:var(--ink-soft);font-size:.95rem;padding:20px;}
  .empty b{color:var(--ink);}

  details{margin-top:20px;border-top:1px solid var(--line);padding-top:14px;}
  summary{cursor:pointer;font-family:var(--font-mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);list-style:none;}
  summary::-webkit-details-marker{display:none;}
  summary::before{content:"▸ ";}
  details[open] summary::before{content:"▾ ";}
  .shelf{display:flex;flex-direction:column;gap:7px;margin-top:12px;}
  .shelf-row{display:flex;justify-content:space-between;gap:10px;font-size:.84rem;padding:7px 10px;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;}
  .shelf-row .nm{color:var(--ink);}
  .shelf-row .rt{font-family:var(--font-mono);font-size:.72rem;color:var(--ink-faint);white-space:nowrap;}
  .shelf-row.rest-done .rt{color:var(--good);}
  .footer-links{display:flex;justify-content:center;gap:18px;margin-top:26px;}
  .footer-links button{font-family:var(--font-mono);font-size:.72rem;color:var(--accent);background:none;border:0;cursor:pointer;}
  .footer-links button:hover{text-decoration:underline;}
  :focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>

<div class="wrap">
  <p class="brand">SF Adventures</p>
  <h1>What should we do <em>today?</em></h1>
  <p class="sub">Tell it how much time you've got, then draw a card. Do it and it rests for a while; skip it and it's back soon.</p>

  <div class="controls">
    <div class="seg" id="timeSeg">
      <button data-t="surprise" aria-pressed="true">Surprise me</button>
      <button data-t="1hr" aria-pressed="false">~1 hr</button>
      <button data-t="4hr" aria-pressed="false">~4 hrs</button>
      <button data-t="all-day" aria-pressed="false">All day</button>
      <button data-t="multi-day" aria-pressed="false">Getaway</button>
    </div>
    <button class="toggle" id="nearToggle" aria-pressed="false"><span class="switch"></span> Near home only</button>
  </div>

  <div class="stage" id="stage"></div>

  <div class="stats" id="stats"></div>

  <details id="restDetails">
    <summary>Resting deck</summary>
    <div class="shelf" id="shelf"></div>
  </details>

  <div class="footer-links">
    <button id="resetBtn">Reset the deck</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const ACTS = __PAYLOAD__;
const CFG = __CFG__;
const CATVAR = {"Outdoorsy & scenic":"--cat-out","Food & drink":"--cat-food","Arts & culture":"--cat-arts","Playful & active":"--cat-play"};
const TIMELBL = {"1hr":"~1 hr","4hr":"~4 hrs","all-day":"All day","multi-day":"Getaway"};
const IOLBL = {"indoor":"Indoor","outdoor":"Outdoor","mixed":"Indoor + out"};
const SCOPELBL = {"day-trip":"Day trip","getaway":"Getaway"};
const byId = Object.fromEntries(ACTS.map(a=>[a.id,a]));
const DAY = 86400000;
const KEY = "sfadv_deck_v1";

let store = load();
let ui = { time:"surprise", near:false, current:null };

function load(){ try{ return JSON.parse(localStorage.getItem(KEY)) || {state:{},log:[]}; }catch(e){ return {state:{},log:[]}; } }
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(store)); }catch(e){} }
function now(){ return Date.now(); }

function resting(a){ const s = store.state[a.id]; return s && s.until > now(); }
function eligible(){
  return ACTS.filter(a=>{
    if(resting(a)) return false;
    if(ui.near && !a.nearHome) return false;
    if(ui.time!=="surprise" && a.duration!==ui.time) return false;
    return true;
  });
}

function fmtWhen(ms){
  const days = Math.max(1, Math.round((ms-now())/DAY));
  if(days<14) return "back in "+days+"d";
  if(days<60) return "back in "+Math.round(days/7)+"w";
  if(days<400) return "back in "+Math.round(days/30)+"mo";
  return "back in ~1yr";
}

function pill(a){
  const chips = [`<span class="tag cost">${a.cost}</span>`,`<span class="tag">${IOLBL[a.io]||a.io}</span>`];
  if(a.reservation==="required") chips.push(`<span class="tag resv">Reserve required</span>`);
  else if(a.reservation==="recommended") chips.push(`<span class="tag resv">Reserve ahead</span>`);
  if(a.season && a.season!=="Year-round") chips.push(`<span class="tag">${a.season}</span>`);
  if(a.withFriends) chips.push(`<span class="tag">Great w/ friends</span>`);
  if(a.stops) chips.push(`<span class="tag">${a.stops}-stop crawl</span>`);
  const tag = a.nearHome ? `<span class="near-tag">near home</span>`
            : (SCOPELBL[a.scope]?`<span class="scope-tag">${SCOPELBL[a.scope]}</span>`:"");
  return `<div class="card anim-in" style="--catc:var(${CATVAR[a.category]})">
    <div class="card-top"><span class="cat">${a.category}</span><span class="time">${TIMELBL[a.duration]}</span></div>
    <h2>${a.name}</h2>
    <div class="hood"><span class="dot"></span>${a.neighborhood} ${tag}</div>
    <p>${a.description}</p>
    <div class="chips">${chips.join("")}</div>
  </div>
  <div class="actions">
    <button class="btn-did" id="didBtn">✅ We did this</button>
    <button class="btn-skip" id="skipBtn">⏭️ Skip</button>
  </div>`;
}

function draw(){
  const pool = eligible();
  const stage = document.getElementById("stage");
  if(!pool.length){
    ui.current = null;
    const soon = ACTS.filter(a=>resting(a)).sort((x,y)=>store.state[x.id].until-store.state[y.id].until)[0];
    stage.innerHTML = `<div class="empty">Everything in this filter is resting right now.<br>
      Try a different amount of time, turn off <b>near home</b>, or check back later.
      ${soon?`<br><br>Next one back: <b>${byId[soon.id].name}</b> (${fmtWhen(store.state[soon.id].until)}).`:""}</div>
      <button class="draw-btn" id="drawAgain" style="margin-top:16px">Try again</button>`;
    const da=document.getElementById("drawAgain"); if(da) da.onclick=draw;
    render(); return;
  }
  const a = pool[Math.floor(Math.random()*pool.length)];
  ui.current = a.id;
  stage.innerHTML = pill(a);
  document.getElementById("didBtn").onclick = ()=>act("done");
  document.getElementById("skipBtn").onclick = ()=>act("skip");
  render();
}

function act(kind){
  const a = byId[ui.current]; if(!a) return;
  const days = (kind==="done"?CFG.doCooldownDays:CFG.skipCooldownDays)[a.duration];
  store.state[a.id] = { until: now()+days*DAY, kind };
  if(kind==="done"){ store.log.unshift({id:a.id, at:now()}); toast("Nice — "+a.name+" done! 🎉"); }
  save();
  draw(); // deal a replacement
}

function showDeckFront(){
  const stage = document.getElementById("stage");
  const n = eligible().length;
  stage.innerHTML = `<div class="facedown">🎴</div>
    <button class="draw-btn" id="drawBtn">Draw my adventure</button>
    <div class="deck-hint">${n} card${n===1?"":"s"} ready in this filter</div>`;
  document.getElementById("drawBtn").onclick = draw;
}

function render(){
  // stats
  const restCount = ACTS.filter(resting).length;
  const ready = eligible().length;
  const done = store.log.length;
  document.getElementById("stats").innerHTML =
    `<span><b>${ready}</b> ready</span><span><b>${restCount}</b> resting</span><span><b>${done}</b> done</span>`;
  // shelf
  const rest = ACTS.filter(resting).sort((x,y)=>store.state[x.id].until-store.state[y.id].until);
  const sh = document.getElementById("shelf");
  if(!rest.length){ sh.innerHTML = `<div class="empty" style="padding:8px">Nothing resting yet — the whole deck is live.</div>`; }
  else sh.innerHTML = rest.map(a=>{
    const s = store.state[a.id];
    return `<div class="shelf-row ${s.kind==='done'?'rest-done':''}"><span class="nm">${a.name}</span>
      <span class="rt">${s.kind==='done'?'✓ ':''}${fmtWhen(s.until)}</span></div>`;
  }).join("");
  document.querySelector("#restDetails summary").textContent =
    `Resting deck (${rest.length})`;
}

let toastT;
function toast(msg){
  const t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show");
  clearTimeout(toastT); toastT=setTimeout(()=>t.classList.remove("show"),2200);
}

// wire controls
document.querySelectorAll("#timeSeg button").forEach(b=>b.onclick=()=>{
  ui.time=b.dataset.t;
  document.querySelectorAll("#timeSeg button").forEach(x=>x.setAttribute("aria-pressed",x===b));
  if(ui.current) draw(); else showDeckFront();
});
const nb=document.getElementById("nearToggle");
nb.onclick=()=>{ ui.near=!ui.near; nb.setAttribute("aria-pressed",ui.near); if(ui.current) draw(); else showDeckFront(); };
document.getElementById("resetBtn").onclick=()=>{
  if(confirm("Reset the whole deck? This clears all cooldowns and history.")){
    store={state:{},log:[]}; save(); ui.current=null; showDeckFront(); render();
  }
};

showDeckFront();
render();
</script>
"""
html = html.replace("__PAYLOAD__", payload).replace("__CFG__", cfg)
out = "preview/today.html"
open(out,"w").write(html)
print("wrote", out, len(html), "bytes")
