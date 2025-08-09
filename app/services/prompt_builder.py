# services/prompt_builder.py
from typing import List, Dict
from .llm import gemini_generate


# ─────────────────────────  SHARED RULES  ──────────────────────────
COMMON_RULES = """
COMMON RULES
1. Generate only the sections the user asked for: {requested_modes_str}
      hooks • punchlines • acts • vibe-reset • clarifying-Qs
2. If a section is NOT requested, omit it entirely.
3. Never rewrite slide text verbatim; reference it like [Slide 7].
4. Bullet limits: Hook ≤20 words, Punchline ≤25, Clarifying-A ≤25.
5. Tie every suggestion to exactly ONE MEET value ({meet_values}).
6. Output *plain text* – no markdown, no numbering outside the bullets.
"""

# ─────────────────────────  TEMPLATES  ─────────────────────────────
HIGHLIGHT_TEMPLATE = """
# MEET – Highlight Script Outline (multi-slide)

CONTEXT
• MEET values……….. {meet_values}
• Instructor style…. {instructor_style}
• Context flags……. {context_flags}
• Custom ideas……. {custom_ideas}
• Instructor notes… {free_text_notes}

SLIDES (flat text)
{slides_text}

{common_rules}

FORMAT
For each time block use:
[MM:SS–MM:SS] <SectionName> – <One-line label>
• Goal: …
• Instructor Actions / Lines: …
• MEET Value Tie-In: …

TOTAL length ≤600 tokens.

BEGIN!
"""

SLIDE_ALIGNED_TEMPLATE = """
# MEET – Per-Slide Teaching Script

CONTEXT
• MEET values……….. {meet_values}
• Instructor style…. {instructor_style}
• Context flags……. {context_flags}
• Custom ideas……. {custom_ideas}
• Instructor notes… {free_text_notes}

SLIDES (text only, no images)
{slides_dump}

{common_rules}

FORMAT
For EACH slide i = 1..{n_slides} output block:

[Slide {{i}}]              
Hook: …
Punchline: …
Acts:
1) …
Clarifying-Qs:
Q: …?  A: …
MEET Value: …

If the slide needs assets add at end:
Missing support: slides_needed=[…], props=[…]

BEGIN!
"""

# ─────────────────────────  UTILITIES  ─────────────────────────────
def preprocess_free_text(free_texts: List[str]) -> str:
    lines = [f"- {ln.strip(' -•')}"
             for txt in free_texts or []
             for ln in (txt or "").splitlines()
             if ln.strip()]
    return "\n".join(lines[:30])


def ai_refine_notes(raw_notes: List[str]) -> str:
    joined = "\n".join(raw_notes or [])
    if not joined.strip():
        return ""
    prompt = (
        "Rewrite the following instructor notes into ≤8 crisp bullets, "
        "≤20 words each, no trailing punctuation:\n\n" + joined
    )
    return (gemini_generate(prompt) or "").strip()

# ─────────────────────────  BUILDERS  ──────────────────────────────
def build_highlight_prompt(
        meet_values: List[str],
        slides_text: str,
        instructor_style: List[str],
        requested_modes: List[str],
        context_flags: Dict,
        custom_ideas: List[str],
        free_text_notes: str) -> str:

    return HIGHLIGHT_TEMPLATE.format(
        meet_values=", ".join(meet_values or []),
        slides_text=slides_text[:8000] or "(no slide text)",
        instructor_style=", ".join(instructor_style or []) or "(neutral)",
        requested_modes_str=", ".join(requested_modes or ["hooks"]),
        context_flags=context_flags,
        custom_ideas=", ".join(custom_ideas or []) or "(none)",
        free_text_notes=free_text_notes or "(none)",
        common_rules=COMMON_RULES.format(
            requested_modes_str=", ".join(requested_modes or ["hooks"]),
            meet_values=", ".join(meet_values or [])
        )
    )


def build_slide_aligned_prompt(
        meet_values: List[str],
        slide_texts: List[str],
        instructor_style: List[str],
        requested_modes: List[str],
        context_flags: Dict,
        custom_ideas: List[str],
        free_text_notes: str) -> str:

    # -- compact slide dump, max 1000 chars per slide
    capped = []
    for i, txt in enumerate(slide_texts or [], 1):
        txt = (txt or "").strip().replace("\r", "")
        if len(txt) > 1000:
            txt = txt[:1000] + " …"
        capped.append(f"Slide {i}:\n{txt}\n")
    slides_dump = "\n".join(capped) or "Slide 1:\n(Empty)"

    return SLIDE_ALIGNED_TEMPLATE.format(
        meet_values=", ".join(meet_values or []),
        instructor_style=", ".join(instructor_style or []) or "(neutral)",
        context_flags=context_flags,
        custom_ideas=", ".join(custom_ideas or []) or "(none)",
        free_text_notes=free_text_notes or "(none)",
        slides_dump=slides_dump,
        n_slides=max(len(slide_texts), 1),
        common_rules=COMMON_RULES.format(
            requested_modes_str=", ".join(requested_modes or ["hooks"]),
            meet_values=", ".join(meet_values or [])
        )
    )
