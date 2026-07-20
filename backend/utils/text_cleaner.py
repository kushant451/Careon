import re

def clean(text):
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def truncate(text, max_chars=3000):
    return text[:max_chars] + "..." if len(text) > max_chars else text

def word_count(text):
    return len(text.split())