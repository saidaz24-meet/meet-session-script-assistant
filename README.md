MEET Session Script Assistant (MSSA)

Slide-aligned, values-driven teaching aide for MEET instructors.
Upload slides → select modes (Hooks, Punchlines, Acts, Clarifying-Qs, Vibe-Reset) → get concise, MEET-value-tied scripts aligned per slide. Built to cut prep time while keeping the spirit of MEET front and center.

✨ What it does

Slide ingestion: Upload a PDF/PPTX; the app extracts per-slide text and renders slide images for preview.

Config → Prompt: Choose modes, MEET values, instructor style, context flags (post_DU, last_session_of_day, mixed_skill, instructor_count), and add free-text notes.

Two generation modes

Per-slide script: [Slide N] blocks with Hook, Punchline, Acts, Clarifying-Qs, Value tie-in (+ optional Vibe-Reset).

Highlight outline (timed blocks): Goal, Instructor Actions, Value tie-in (+ branches for on-time / behind / low-energy).

Viewer UI:

Right: slide image & navigation.

Left: expandable cards per section (Hooks, Punchlines, etc.). Each card shows compact options as pills; clicking a pill opens a detailed overlay (purpose/why).

Email share: Send the currently open card (or all cards on a slide) via SMTP.

Auth & storage: Firebase Authentication (client) + Firebase Admin (server) for secure sessions and persistence.

🧭 Why it exists

MEET’s pedagogy is binational, interactive, and values-forward—but instructors lose time scripting and reinventing engagement. MSSA keeps values embedded in the flow while saving prep time, so teaching can be energetic, safe, and coherent across the team.

🗺️ Architecture (high level)
Client (Flask+Jinja, JS, CSS)
   ├── /upload           → PDF/PPTX → server extracts text + slide images
   ├── /configure        → modes, values, style, context, ideas, notes
   ├── /generate         → renders Viewer (slides + expandable cards)
   └── /auth/*           → signup/login; server session via Firebase ID token

Server (Flask)
   ├── services/extractor.py      # structured text from slides
   ├── services/renderer.py       # slide images
   ├── services/converter.py      # PPTX → images
   ├── services/prompt_builder.py # robust Gemini prompts (per-slide / highlight)
   ├── services/llm.py            # gemini_generate()
   ├── services/storage.py        # Firestore session docs
   └── routes/{web,api,auth}.py

Firebase
   ├── Client: Auth (email/password)
   └── Server: Admin SDK (verify token, Firestore)

🔧 Requirements

Python 3.10+

Pip + virtualenv (or python -m venv)

Poppler (if your renderer depends on it for PDF → images) (macOS: brew install poppler)

LibreOffice (only if you configure PPTX rendering through soffice) — optional

The repo’s services/renderer.py / converter.py handle images; if you change the backend, install the matching system deps.

🚀 Quick start (local)
git clone https://github.com/<you>/meet-session-script-assistant.git
cd meet-session-script-assistant

python3 -m venv myenv
source myenv/bin/activate        # Windows: myenv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env             # create .env and fill secrets (see below)

python run.py
# App runs at http://127.0.0.1:5000


Login flow:

Visit /auth/signup (or /auth/login).

After signup/login, go to /upload → choose PDF/PPTX.

Continue to /configure, set modes/values/style/context.

Click Generate → /generate shows the Viewer.

Keyboard: ← / → to change slides.
Click pills to open detailed overlays; ✉ Send emails the open card (or the full left pane if no card is open).
