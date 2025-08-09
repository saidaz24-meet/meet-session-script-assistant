/* ────────────────────────────────────────────────────────────────
   MEET Session Viewer  –  slide images (R) | script cards (L)
   ──────────────────────────────────────────────────────────────── */

/* ---------- DOM refs ---------- */
const slideBox = document.getElementById("slidePreview");
const winArea  = document.getElementById("windows");
const counter  = document.getElementById("slideCounter");
const prevBtn  = document.getElementById("prevBtn");
const nextBtn  = document.getElementById("nextBtn");
const emailBtn = document.getElementById("emailBtn");

/* ---------- globals injected by Jinja ---------- */
const DATA   = JSON.parse(document.getElementById("viewer-data").textContent);
const IMG    = DATA.images || [];
const RAW    = DATA.script || "";
const MODES  = (DATA.modes || []).map(s => s.toLowerCase());
const SHOW_ALL = MODES.includes("full-highlight-script");   // bypass mode-filter if user asked for everything

/* ---------- state ---------- */
let idx = 0;          // current slide index
let segments = [];    // [{slide, text}]

/* ───────────── helpers ───────────── */

/* Split Gemini output by [Slide N]  */
function splitBySlide(raw){
  const out = [], re = /\[Slide\s*(\d+)]/gi;
  let m, last = 0, cur = 1;
  if(!re.test(raw)) return [{slide:1,text:raw.trim()}];
  re.lastIndex = 0;
  while((m = re.exec(raw)) !== null){
    if(m.index > last) out.push({slide:cur,text:raw.slice(last,m.index).trim()});
    cur = +m[1]; last = re.lastIndex;
  }
  out.push({slide:cur,text:raw.slice(last).trim()});
  return out.filter(o=>o.text);
}

/* Canonical section map → hooks | punchlines | acts | vibe-reset | clarifying-qs */
const CANON = {
  hook:"hooks", hooks:"hooks",
  punchline:"punchlines", "punchline idea":"punchlines", punchlines:"punchlines",
  act:"acts", acts:"acts",
  "vibe reset":"vibe-reset","vibe-reset":"vibe-reset",
  clarifying:"clarifying-qs","clarifying qs":"clarifying-qs","clarifying-q":"clarifying-qs","clarifying-qs":"clarifying-qs"
};
const norm = t => CANON[t.trim().toLowerCase()] || t.trim().toLowerCase().replace(/\s+/g,"-");

/* Pretty labels for card headers */
const PRETTY = {
  "hooks"          : "Hooks",
  "punchlines"     : "Punchlines",
  "acts"           : "Acts",
  "q":"Questions",
  "vibe-reset"     : "Vibe Reset",
  "clarifying-qs"  : "Questions",
  "script"         : "Script"
};
const nice = k => PRETTY[k] || (k.charAt(0).toUpperCase() + k.slice(1));

/* Robust parser – handles block AND flat-line styles */
function parseWindows(txt){
  const out = Object.create(null);
  let structured = false;

  /* A) Block style: **Hooks**:\n1) … */
  txt.split(/\n{2,}/).forEach(block=>{
    const m = block.match(/^\s*\*{0,2}([\w\- ]+?)\*{0,2}\s*:/i);
    if(!m) return;
    structured = true;
    const key = norm(m[1]);
    if(!SHOW_ALL && MODES.length && !MODES.includes(key)) return;

    const items = block.replace(m[0],'').trim()
                       .split(/\n\d+\)/).map(t=>t.trim()).filter(Boolean)
                       .map(x=>{
                         const [sum,purp=''] = x.split(/\n\s*Purpose:/i);
                         return {summary:sum.trim(), purpose:purp.trim()};
                       });
    if(items.length) out[key]=(out[key]||[]).concat(items);
  });

  /* B) Flat style: Hook: … / Punchline: … */
  txt.split(/\n+/).forEach(line=>{
    const m = line.match(/^\s*([\w\- ]+?):\s*(.+)$/);
    if(!m) return;
    structured = true;
    const key = norm(m[1]);
    if(!SHOW_ALL && MODES.length && !MODES.includes(key)) return;
    (out[key]=out[key]||[]).push({summary:m[2].trim(),purpose:""});
  });

  /* fallback – dump everything into one card */
  if(!structured && txt.trim()){
    out.script=[{summary:txt.slice(0,160)+(txt.length>160?" …":""),purpose:""}];
  }
  return out;
}

/* ───────────── rendering ───────────── */

/* right pane – slide */
function renderSlide(){
  slideBox.innerHTML = IMG[idx]
    ? `<img src="${IMG[idx]}" alt="Slide ${idx+1}">`
    : `<div class="placeholder muted">No slide image</div>`;
  counter.textContent = `${idx+1} / ${Math.max(IMG.length,1)}`;
}

/* pill-card factory */
function makeCard(rawKey, arr){
  const pills = arr.map((_,i)=>`<button class="pill" data-i="${i}">${i+1}</button>`).join("");
  const card  = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <header>${nice(rawKey)}</header>
    <div class="pill-row">${pills}</div>
    <div class="overlay">
      <button class="close">×</button>
      <div class="detail"></div>
    </div>`;

  card.querySelectorAll(".pill").forEach(btn=>{
    btn.onclick = ()=>{
      const o = arr[+btn.dataset.i];
      card.querySelector(".detail").innerHTML =
        `<h4>${o.summary}</h4><p>${o.purpose}</p>`;
      card.classList.add("open");
    };
  });
  card.querySelector(".close").onclick = e=>{
    e.stopPropagation(); card.classList.remove("open");
  };
  return card;
}

/* left pane – windows */
function renderWindows(){
  winArea.style.opacity = 0;
  winArea.innerHTML = "";
  const slideNum = idx+1;
  const seg = segments.find(s=>s.slide===slideNum)
             || segments.find(s=>s.slide<=slideNum)
             || segments[0];

  if(!seg){winArea.textContent="(no script)";return;}

  const map = parseWindows(seg.text);
  Object.entries(map).forEach(([key,list])=>{
    winArea.appendChild(makeCard(key,list));
  });
  requestAnimationFrame(()=> winArea.style.opacity = 1);
}

/* ───────────── navigation ───────────── */
function goto(i){
  const max = Math.max(IMG.length, segments.length, 1);
  if(i<0||i>=max) return;
  idx=i; renderSlide(); renderWindows();
}
prevBtn.onclick = ()=>goto(idx-1);
nextBtn.onclick = ()=>goto(idx+1);
document.addEventListener("keydown",e=>{
  if(e.key==="ArrowLeft") prevBtn.click();
  if(e.key==="ArrowRight")nextBtn.click();
});

/* ───────────── email send ───────────── */
emailBtn.onclick=async()=>{
  const to=prompt("Recipient email:"); if(!to) return;
  const open=winArea.querySelector(".card.open .overlay");
  const html=open?open.outerHTML:winArea.innerHTML;
  try{
    const r=await fetch("/api/email",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({to,subject:`MEET Script — Slide ${idx+1}`,html})
    });
    if(!r.ok) throw new Error((await r.json()).detail||"Send failed");
    alert("Email sent!");
  }catch(err){alert(err.message);}
};

/* ───────────── boot ───────────── */
segments = splitBySlide(RAW);
if(!segments.length) segments=[{slide:1,text:"(no script)"}];
goto(0);
