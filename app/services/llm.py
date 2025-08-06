import logging
import google.generativeai as genai
from ..config import Config

log = logging.getLogger(__name__)

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    log.info("Gemini configured ✅ model=%s", Config.MODEL_NAME)
else:
    log.warning("GEMINI_API_KEY missing — fallback text will be used ❗")

def gemini_generate(prompt: str) -> str:
    if not Config.GEMINI_API_KEY:
        log.warning("gemini_generate(): fallback text path used")
        return (
            "[00:00-05:00] Arrival Reset [Slide 1]\n"
            "- Goal: Decompress after DU; reset norms\n"
            "- Instructor: Play music; phones in bags; laptops closed\n"
            "- Value: Respect; shared norms\n"
            "Missing support: slides_needed=[\"MVC diagram\"], props=[\"markers\"]\n"
        )
    try:
        model = genai.GenerativeModel(Config.MODEL_NAME)
        resp = model.generate_content(prompt)
        out = (resp.text or "").strip()
        log.info("gemini_generate(): %d chars returned", len(out))
        return out
    except Exception as e:
        log.exception("Gemini call failed: %s", e)
        # Surface a short error so you can see it in the UI if desired
        return f"[ERROR] Gemini call failed: {e}"

def gemini_condense_chat(messages: list[dict]) -> str:
    if not Config.GEMINI_API_KEY:
        bullets = "\n".join(f"- {m['role']}: {m['content'][:140]}" for m in messages[-10:])
        return f"## Chat Summary\n{bullets}\n"
    try:
        model = genai.GenerativeModel(Config.MODEL_NAME)
        prompt = "Condense the following instructor chat into goals, style cues, and constraints:\n"
        content = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-20:]])
        resp = model.generate_content(prompt + content)
        return (resp.text or "").strip()
    except Exception as e:
        log.exception("Gemini condense failed: %s", e)
        return ""
