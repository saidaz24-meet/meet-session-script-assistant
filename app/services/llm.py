import google.generativeai as genai
from ..config import Config

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

def generate_from_gemini(prompt: str) -> str:
    # Graceful fallback if no key provided (for local dev)
    if not Config.GEMINI_API_KEY:
        return (
            "[00:00-05:00] Arrival Reset\n"
            "- Goal: Decompress after DU; reset norms\n"
            "- Instructor: Play music; phones in bags; laptops closed\n"
            "- Value: Respect; shared norms\n"
            "Missing support: slides_needed=[], props=[]\n"
        )
    model = genai.GenerativeModel(Config.MODEL_NAME)
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()
