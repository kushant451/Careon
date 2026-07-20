import json, re

def clean_json_block(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

def safe_json_loads(text):
    try:
        return json.loads(clean_json_block(text))
    except (json.JSONDecodeError, TypeError):
        return None

def stars(score, out_of=10.0):
    filled = round((score / out_of) * 5)
    return "★" * filled + "☆" * (5 - filled)

def percent(part, total):
    return round((part / total) * 100) if total else 0