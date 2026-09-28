import re
import requests
from app.config.settings import settings

def tokens(text):
    return set(re.findall(r"[a-zA-Z0-9]+", (text or "").lower()))

def keyword_match(user_text, schemes):
    q = tokens(user_text)
    scored = []
    for s in schemes:
        hay = " ".join([
            s.get("name",""), s.get("description",""), s.get("benefit",""),
            s.get("category",""), s.get("business_keywords","")
        ])
        score = len(q & tokens(hay))
        scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored

def llm_match(user_text, schemes):
    if not settings.ai_enabled or not settings.openai_api_key or not settings.openai_model:
        return None
    prompt = """You are a semantic matching assistant. Return JSON array of scheme ids and short reasons.
Never invent eligibility rules, benefits, amounts or official facts. Use only the supplied scheme records.
User request:
%s

Schemes:
%s
""" % (user_text, schemes)
    try:
        r = requests.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
            json={"model": settings.openai_model, "messages":[{"role":"user","content":prompt}], "temperature":0},
            timeout=20
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None
