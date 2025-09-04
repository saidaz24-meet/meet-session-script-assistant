### MEET Session Script Assistant (MSSA) 🍍

Turn slide decks into **slide-aligned, values-driven teaching flows**.  
Hooks, punchlines, acts, clarifying-Qs, vibe-resets—only the parts you choose, all tied to MEET’s spirit 🌱.

Upload slides → pick modes & values → get compact, per-slide options you can teach from.  

---

## 💡 Why It Was Built

This started in a MEET summer: I served as a CS TA for Y2 (10th grade), spending ~12 hours a day with students and another ~2 hours every night writing scripts for the next session.  

I loved the work—watching binational pairs debug together and light up when ideas clicked—but I kept seeing the same pain points:

- 😵 Students lose focus when content isn’t interactive or adaptive to the room’s energy.  
- ⏳ Instructors burn time inventing hooks, activities, and transitions from scratch.  
- 🌍 Values aren’t embedded consistently—the *how* of teaching MEET (respect, collaboration, ownership) sometimes slips under pressure.  
- 💸 Post-war constraints (budget, turnover) mean new instructors don’t always get deep pedagogy onboarding.  

I interviewed leadership + instructors and narrowed the problem:  
👉 we needed a way to **bake MEET’s values directly into the teaching flow**—inside the hook, the act, the clarifying question—per slide, per room.

**MSSA** is that assistant. It reads the slide text + your choices (modes, values, style), and returns short, teachable options aligned to each slide—with the purpose/why and the MEET value explicit.  

🎯 **Goal**: Free instructor judgment. Less time scripting → more time with students.  

Piloted with instructors, feedback was encouraging, and the Student Director is open to including it next year—reaching 120+ students and supporting 12+ CS instructors (including me). That’s the impact target. 🍓

---

## ✨ What It Does

- 📇 Left: cards per section (Hooks / Punchlines / Acts / Clarifying-Qs / Vibe-Reset) with multiple pills (suggestions).  
- 🖼️ Right: live slide preview with arrow-key navigation.  
- 👆 Click a pill → sleek overlay with the *purpose/why* behind that suggestion.  
- 📧 Email the open card to yourself or a co-instructor.  
- 🔒 Strict prompts: plain text, short bullets, grounded in slide text, each suggestion tied to one MEET value.  

⚠️ Privacy note: the LLM sees *text only* (slide text + your configuration), not slide images.  

---

## ⚡ Quick Start

```bash
git clone https://github.com/<your-username>/mssa
cd mssa
python3 -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # or create .env and fill values below
python run.py          # open http://127.0.0.1:5000
```
🌀 Flow
✍️ Sign up / log in (email + password).

📂 Upload PDF/PPTX → app extracts text & renders slide images.

⚙️ Configure: choose modes, values, instructor style, context flags.

🎬 Generate → Viewer opens. Use ←/→; click pills to expand.

🧠 How It Works (Tiny)
Slides → Extract text → Build prompt from your choices
→ Gemini returns: [Slide N] … Hook / Punchline / Acts …
→ Viewer shows cards (left) + slide preview (right)

🎯 Tips for Great Outputs
Use decks with clear slide text (headings + concise bullets).

Select just the modes you need (less = sharper).

Add style keywords (“playful”, “story-driven”, “call-and-response”).

Drop free-text notes for must-include examples or crowd cues.

🛟 Quick Troubleshoot
Left side empty? Ensure at least one mode is selected. Parser handles [Slide N] and Hook: formats.

Images missing? For PDFs, install local PDF rendering deps (e.g., Poppler).

Name shows “None”? After sign-up, we set displayName. Refresh once.

🖼️ Suggested Visuals (for Repo / Pitch Deck)
🖥️ Configure screen (modes/values/style) → “Solution”

🎭 Viewer (slides right, cards left) → “Outputs (MVP)”

🔧 Pipeline sketch (Inputs → LLM → Viewer) → “Under the hood”

🪄 License
MIT — remix it, teach with it, improve it. 🍍
