import json, re
from datetime import datetime

DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def safe_json(text):
    if isinstance(text, dict):
        return text
    text = text.strip()
    # remove markdown fences if the model added them
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

def valid_quiz(data, n):
    if not isinstance(data, dict) or data.get("status") != "ok":
        return False
    qs = data.get("questions")
    if not isinstance(qs, list) or len(qs) != n:
        return False
    for q in qs:
        if not isinstance(q, dict):
            return False
        if not q.get("question") or q.get("answer") not in ["A","B","C","D"]:
            return False
        if not isinstance(q.get("options"), list) or len(q["options"]) != 4:
            return False
    return True

def valid_cards(data, n):
    if not isinstance(data, dict) or data.get("status") != "ok":
        return False
    cards = data.get("cards")
    if not isinstance(cards, list) or len(cards) != n:
        return False
    return all(isinstance(c, dict) and c.get("front") and c.get("back") for c in cards)

def valid_explanation(data):
    return isinstance(data, dict) and data.get("status") == "ok" and all(
        data.get(k) for k in ["topic","difficulty","explanation","example","common_mistake","check"]
    )
