// RIGHT: slide images (if any). LEFT: script for the current slide.
// We split script by [Slide N]. If none, show full script on first slide.

const slidePreview = document.getElementById("slidePreview");
const scriptContainer = document.getElementById("scriptContainer");
const counterEl = document.getElementById("slideCounter");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const emailBtn = document.getElementById("emailBtn");

let idx = 0;
let segments = []; // [{slide:1, text:"..."}, ...]

function splitBySlides(scriptText) {
  // Find [Slide N] markers
  const regex = /\[Slide\s*(\d+)\]/gi;
  let m, lastIndex = 0, current = 1, out = [];
  while ((m = regex.exec(scriptText)) !== null) {
    const slideNum = parseInt(m[1],10);
    if (m.index > lastIndex) {
      // previous chunk belongs to `current`
      const chunk = scriptText.slice(lastIndex, m.index).trim();
      if (chunk) out.push({ slide: current, text: chunk });
    }
    current = slideNum;
    lastIndex = regex.lastIndex;
  }
  // tail
  const tail = scriptText.slice(lastIndex).trim();
  if (tail) out.push({ slide: current, text: tail });

  if (out.length === 0) out.push({ slide: 1, text: scriptText.trim() || "(empty)" });
  return out;
}

function renderSlide(i) {
  const img = VIEWER_IMAGES[i] || null;
  slidePreview.innerHTML = img
    ? `<img src="${img}" alt="Slide ${i+1}"/>`
    : `<div class="muted">No slide image available (try uploading PDF).</div>`;
  counterEl.textContent = `${i+1} / ${Math.max(VIEWER_IMAGES.length, 1)}`;
}

function renderScript(i) {
  const slideNum = i + 1;
  // pick the first segment whose .slide === slideNum, else closest lower
  let seg = segments.find(s => s.slide === slideNum);
  if (!seg) {
    const lowers = segments.filter(s => s.slide <= slideNum);
    seg = lowers.length ? lowers[lowers.length - 1] : segments[0];
  }
  // make transcript-like block with expand section
  scriptContainer.innerHTML = `
    <div class="transcript-block">
      <pre class="details" style="white-space:pre-wrap">${seg.text}</pre>
      <details class="details">
        <summary class="summary">Expand: Guidance & Tips</summary>
        <div style="margin-top:.5rem">
          <p class="muted">Use this section to add your notes or clarifications. (Future: auto-insert clarifying Qs.)</p>
        </div>
      </details>
    </div>
  `;
}

function goto(i) {
    if (i < 0) return;
    const maxSlides = Math.max(VIEWER_IMAGES.length, segments.length, 1); // ← use segments too
    if (i >= maxSlides) return;
    idx = i;
    renderSlide(idx);
    renderScript(idx);
  }
  

prevBtn.addEventListener("click", () => goto(idx - 1));
nextBtn.addEventListener("click", () => goto(idx + 1));

emailBtn.addEventListener("click", async () => {
  const to = prompt("Recipient email:");
  if (!to) return;
  const html = scriptContainer.innerHTML;
  try {
    const res = await fetch("/api/email", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({to, subject:`MEET Script — Slide ${idx+1}`, html})
    });
    const j = await res.json();
    if (!res.ok) throw new Error(j.detail || "Email failed");
    alert("Email sent!");
  } catch(e) {
    alert("Email failed: " + e.message);
  }
});

// Init
segments = splitBySlides(VIEWER_SCRIPT || "");
goto(0);

// Keyboard navigation
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") nextBtn.click();
  if (e.key === "ArrowLeft") prevBtn.click();
});
