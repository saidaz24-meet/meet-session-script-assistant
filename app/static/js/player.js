const slidePreview = document.getElementById("slidePreview");
const transcriptEl = document.getElementById("transcript");
const counterEl = document.getElementById("slideCounter");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const emailBtn = document.getElementById("emailBtn");
let idx = 0;

function renderSlide(i) {
  const s = SLIDES[i] || {};
  slidePreview.innerHTML = `
    <div class="slide">
      ${s.slide_image ? `<img src="${s.slide_image}" alt="${s.slide_title||''}"/>`
                      : `<div class="muted">No slide image — ${s.slide_title||'Untitled'}</div>`}
    </div>
    <h3>${s.slide_title || "Untitled"}</h3>
  `;
  counterEl.textContent = `${i+1} / ${SLIDES.length}`;
}

function renderTranscript(i) {
  const s = SLIDES[i] || {};
  const tx = (s.transcript || []).map(item => `
      <div class="line">
        <span class="speaker">${item.speaker}</span>:
        <span class="editable" contenteditable="true">${item.line}</span>
        <span class="edit-pen" title="edit">✎</span>
      </div>
  `).join("");

  const details = `
    <details class="details">
      <summary class="summary">Expand: Goal & Vision & Full Explanation</summary>
      <div style="margin-top:.5rem">
        ${s.slide_goal ? `<p><b>Slide goal:</b> ${s.slide_goal}</p>` : ``}
        ${s.vision ? `<p><b>Vision:</b> ${s.vision}</p>` : ``}
        ${s.full_explanation ? `<p>${s.full_explanation}</p>` : `<p class="muted">No extended explanation.</p>`}
      </div>
    </details>
  `;

  transcriptEl.innerHTML = `
    <div class="transcript-block">
      ${tx || `<div class="muted">No transcript lines for this slide.</div>`}
      ${details}
    </div>
  `;
}

function goto(i) {
  if (i < 0 || i >= SLIDES.length) return;
  idx = i;
  renderSlide(idx);
  renderTranscript(idx);
}

prevBtn.addEventListener("click", () => goto(idx - 1));
nextBtn.addEventListener("click", () => goto(idx + 1));

emailBtn.addEventListener("click", async () => {
  const to = prompt("Recipient email:");
  if (!to) return;

  const slide = SLIDES[idx] || {};
  const lines = [...transcriptEl.querySelectorAll(".line")].map(lineEl => {
    const speaker = lineEl.querySelector(".speaker").textContent;
    const text = lineEl.querySelector(".editable").textContent;
    return `<p><b>${speaker}:</b> ${text}</p>`;
  }).join("");

  const html = `
    <h2>${slide.slide_title || "Untitled"}</h2>
    ${lines || "<p><i>No lines.</i></p>"}
    <hr/>
    ${slide.slide_goal ? `<p><b>Slide goal:</b> ${slide.slide_goal}</p>` : ``}
    ${slide.vision ? `<p><b>Vision:</b> ${slide.vision}</p>` : ``}
    ${slide.full_explanation ? `<p>${slide.full_explanation}</p>` : ``}
  `;

  try {
    const res = await fetch("/api/email", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({to, subject:`MEET Transcript — ${slide.slide_title||'Slide'}`, html})
    });
    const j = await res.json();
    if (!res.ok) throw new Error(j.detail || "Email failed");
    alert("Email sent!");
  } catch(e) {
    alert("Email failed: " + e.message);
  }
});

// init
if (SLIDES.length === 0) {
  slidePreview.innerHTML = `<div class="muted">No slides found.</div>`;
} else {
  goto(0);
}
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") nextBtn.click();
  if (e.key === "ArrowLeft") prevBtn.click();
});
