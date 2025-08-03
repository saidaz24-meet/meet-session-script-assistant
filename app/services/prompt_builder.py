from typing import List, Dict

TEMPLATE = """## CONTEXT
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

def build_prompt(meet_values: List[str],
                 slides_text: str,
                 instructor_style: List[str],
                 requested_modes: List[str],
                 context_flags: Dict,
                 custom_ideas: List[str]) -> str:
    return TEMPLATE.format(
        meet_values=", ".join(meet_values or []),
        slides_text=slides_text[:8000],  # safety trim
        instructor_style=", ".join(instructor_style or []),
        requested_modes=", ".join(requested_modes or []),
        context_flags=context_flags,
        custom_ideas=", ".join(custom_ideas or []),
    )
