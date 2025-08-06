from typing import List, Dict
from .llm import *


HIGHLIGHT_TEMPLATE = """## CONTEXT
• MEET mission & values: {{MEET_VALUES}}  
• Slides (plain text export, no images): {{SLIDES_TEXT}}  
• Instructor style keywords (tone, voice, quirks): {{INSTRUCTOR_STYLE}}  

## TASK
Generate a **HIGHLIGHT SCRIPT OUTLINE** (not full speaker notes) that blends  
the *why* (MEET culture) with the *what* (slide content). Follow these rules:

1. Output only the sections requested in {{REQUESTED_MODES}}  
   • “hooks” = openers & attention grabs  
   • “punchlines” = memorable one‑liners tied to values  
   • “acts” = physical or collaborative demos stressing binational teamwork  
   • “vibe‑reset” = quick energy boosters backed by research  
   • “clarifying‑Qs” = likely student questions + concise answers  
2. Chunk by time blocks in **[MM:SS‑MM:SS]** format.  
3. Each block must include:  
   – *Goal* (one sentence)  
   – *Instructor Actions / Lines* (bullets, max 25 words each)  
   – *MEET Value Tie‑In* (one phrase)  
4. Do **NOT** rewrite slide content verbatim; reference it in brackets (e.g., [Slide 7]).  
5. Keep total outline under 600 tokens.

## EXAMPLES
### INPUT (excerpt)
Slides text: “Model‑View‑Controller overview …”  
Requested modes: hooks, acts  

### EXPECTED OUTPUT (excerpt)
[00:00‑03:00] Hook – Call‑and‑Response  
• Goal: Re‑center binational energy after DU  
• Actions: Instructor shouts “Roses are red…” → Students reply “Y2!”  
• Value: Shared identity across cohorts  

(End example)

## DELIVERABLE
Return the outline in plain text; no explanations or markdown.  
When ready, **BEGIN!**

"""

SLIDE_ALIGNED_TEMPLATE = """You are “MEET Session Script Assistant,” a playful but disciplined co-instructor.

CONTEXT
• MEET values: {meet_values}
• Instructor style: {instructor_style}
• Context flags: {context_flags}
• Custom ideas: {custom_ideas}
• Instructor notes (refined): {free_text_notes}

SLIDES (text content)
{slides_dump}

TASK
Produce a slide-aligned teaching script. For EACH slide i = 1..{n_slides}, output a block that STARTS with:
[Slide {slide_index}]
Then include, grounded ONLY in that slide’s content:
- Hook (≤20 words)
- Punchline (≤25 words)
- Acts (1–2 physical/interactive acts that emphasize binational collaboration)
- Clarifying-Qs (1–2 likely questions + concise answers)
- MEET Value Tie-In (short phrase)
- Optional: Vibe Reset if energy likely dips at this slide

STRICTNESS
- Do NOT invent topics not present in the slide’s text.
- Keep each bullet compact.
- Never reference [time ranges]; use only [Slide N] headings.
- If the slide needs assets (visuals/props), add at the end: Missing support: slides_needed=[...], props=[...]

DELIVERABLE
Plain text only. One [Slide N] block per slide in order.
"""


def preprocess_free_text(free_texts: List[str]) -> str:
    bullets = []
    for t in free_texts or []:
        for line in (t or "").splitlines():
            s = line.strip(" -•\t")
            if s:
                bullets.append(f"- {s}")
    return "\n".join(bullets[:30])

def ai_refine_notes(raw_notes: List[str]) -> str:
    joined = "\n".join(raw_notes or [])
    if not joined.strip():
        return ""
    refinement_prompt = (
        "Rewrite the following instructor notes into ≤8 crisp bullet points, "
        "each ≤20 words, no trailing punctuation:\n\n"
        f"{joined}"
    )
    bullets = gemini_generate(refinement_prompt)
    return (bullets or "").strip()

def build_highlight_prompt(meet_values: List[str],
                           slides_text: str,
                           instructor_style: List[str],
                           requested_modes: List[str],
                           context_flags: Dict,
                           custom_ideas: List[str],
                           free_text_notes: str) -> str:
    return HIGHLIGHT_TEMPLATE.format(
        meet_values=", ".join(meet_values or []),
        slides_text=slides_text[:8000],
        instructor_style=", ".join(instructor_style or []),
        requested_modes=", ".join(requested_modes or []),
        context_flags=context_flags,
        custom_ideas=", ".join(custom_ideas or []),
        free_text_notes=free_text_notes
    )

def build_slide_aligned_prompt(meet_values: List[str],
                               slide_texts: List[str],
                               instructor_style: List[str],
                               requested_modes: List[str],
                               context_flags: Dict,
                               custom_ideas: List[str],
                               free_text_notes: str) -> str:
    # Compact dump: cap each slide to ~1000 chars to keep prompt small
    capped = []
    for i, s in enumerate(slide_texts):
        text = (s or "").strip().replace("\r", "")
        if len(text) > 1000:
            text = text[:1000] + " …"
        capped.append(f"Slide {i+1}:\n{text}\n")
    slides_dump = "\n".join(capped) if capped else "Slide 1:\n(Empty)"

    return SLIDE_ALIGNED_TEMPLATE.format(
        meet_values=", ".join(meet_values or []),
        instructor_style=", ".join(instructor_style or []),
        context_flags=context_flags,
        custom_ideas=", ".join(custom_ideas or []),
        free_text_notes=free_text_notes,
        slides_dump=slides_dump,
        n_slides=len(slide_texts) or 1,
        slide_index="{i}"  # not used; kept for readability of spec
    )