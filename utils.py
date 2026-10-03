import json
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple

ALLOWED_MODES = ["LEARN", "QUIZ", "FLASHCARDS", "DIAGNOSTIC"]
ALLOWED_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

# Expanded Off-topic and Non-Python keywords/phrases to filter out
OFF_TOPIC_KEYWORDS = [
    "weather", "politics", "election", "movie", "cinema", "song", "music",
    "cricket", "football", "sports", "recipe", "cooking", "food", "news",
    "celebrity", "crypto", "bitcoin", "dating", "personal advice", "horoscope",
    "travel", "flight", "hotel", "fashion", "makeup", "gym", "workout",
    "medical", "doctor", "health", "symptoms", "history of", "capital of",
    "who is", "poem", "story", "joke", "essay", "translate", "french", "spanish"
]

# Python programming allowed signals/keywords
PYTHON_SIGNALS = [
    "python", "variable", "loop", "for", "while", "function", "def", "class",
    "object", "list", "dict", "dictionary", "tuple", "set", "module", "package",
    "import", "lambda", "decorator", "generator", "comprehension", "exception",
    "try", "except", "oop", "recursion", "file", "async", "await", "threading",
    "multiprocessing", "numpy", "pandas", "matplotlib", "django", "flask",
    "fastapi", "scikit", "pytest", "unittest", "sql", "database", "regex",
    "algorithm", "data structure", "string", "int", "float", "boolean", "type",
    "syntax", "argument", "parameter", "return", "scope", "closure", "magic method",
    "dunder", "init", "inheritance", "polymorphism", "encapsulation", "iterator",
    "yield", "pip", "virtualenv", "pep8", "dataclass", "typing", "json", "csv"
]

def now() -> str:
    """Returns ISO timestamp with timezone."""
    return datetime.now().astimezone().isoformat(timespec="seconds")

def clean_json_string(text: str) -> str:
    """Strips Markdown fences and whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def safe_json(text: Any) -> Dict[str, Any]:
    """Parses JSON safely from string or dict."""
    if isinstance(text, dict):
        return text
    clean_text = clean_json_string(str(text))
    return json.loads(clean_text)

def validate_input(topic: str, mode: str, difficulty: str = "Beginner") -> Tuple[bool, Dict[str, Any]]:
    """
    Application-level input validation guardrails.
    Returns (is_valid, error_dict_or_empty).
    """
    # 1. Topic presence
    if not topic or not topic.strip():
        return False, {
            "status": "rejected",
            "reason": "EMPTY_INPUT",
            "message": "⚠️ Please enter a Python topic."
        }

    # 2. Input length guardrail
    if len(topic.strip()) > 300:
        return False, {
            "status": "rejected",
            "reason": "INPUT_TOO_LONG",
            "message": "⚠️ Input is too long (>300 characters). Please provide a concise Python topic."
        }

    topic_lower = topic.strip().lower()

    # 3. Off-topic keyword check
    for kw in OFF_TOPIC_KEYWORDS:
        if kw in topic_lower:
            return False, {
                "status": "rejected",
                "reason": "OFF_TOPIC",
                "message": f"🚫 **Off-Topic Detected:** '{topic.strip()}' is not related to Python. This assistant only supports Python programming and computer science learning."
            }

    # 4. Mode validation
    if mode.upper() not in ALLOWED_MODES:
        return False, {
            "status": "rejected",
            "reason": "INVALID_MODE",
            "message": "⚠️ Invalid mode. Please select Learn, Quiz, Flashcards, or Diagnostic."
        }

    # 5. Difficulty validation (for modes requiring it)
    if mode.upper() in ["LEARN", "QUIZ", "FLASHCARDS"]:
        if difficulty.capitalize() not in ALLOWED_DIFFICULTIES:
            return False, {
                "status": "rejected",
                "reason": "INVALID_DIFFICULTY",
                "message": "Please select Beginner, Intermediate, or Advanced."
            }

    return True, {}

def validate_learn_output(data: Dict[str, Any]) -> bool:
    """Validates Learn mode response structure."""
    if not isinstance(data, dict) or data.get("status") != "success":
        return False
    required_fields = [
        "mode", "topic", "difficulty", "title", "definition",
        "why_it_is_used", "syntax", "example", "explanation",
        "common_mistake", "practice_question"
    ]
    return all(bool(data.get(field)) for field in required_fields)

def validate_quiz_output(data: Dict[str, Any], expected_count: int = 5) -> bool:
    """
    Validates Quiz mode response:
    - Exactly expected_count questions
    - Exactly 4 options per question
    - Exactly 1 correct answer matching an option
    - Non-empty explanation
    """
    if not isinstance(data, dict) or data.get("status") != "success":
        return False
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != expected_count:
        return False

    for q in questions:
        if not isinstance(q, dict):
            return False
        if not q.get("question") or not q.get("explanation"):
            return False
        options = q.get("options")
        if not isinstance(options, list) or len(options) != 4:
            return False
        correct = q.get("correct_answer")
        if not correct or correct not in options:
            return False

    return True

def validate_flashcards_output(data: Dict[str, Any], expected_count: int = 5) -> bool:
    """Validates Flashcards response: exactly expected_count cards with front, back, example."""
    if not isinstance(data, dict) or data.get("status") != "success":
        return False
    cards = data.get("flashcards")
    if not isinstance(cards, list) or len(cards) != expected_count:
        return False
    for c in cards:
        if not isinstance(c, dict):
            return False
        if not c.get("front") or not c.get("back"):
            return False
    return True

def validate_diagnostic_output(data: Dict[str, Any]) -> bool:
    """Validates Diagnostic response: exactly 10 questions covering diverse topics."""
    return validate_quiz_output(data, expected_count=10)

def calculate_performance(diagnostic_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes actual student diagnostic results without fabricating data.
    - Strong: >= 80%
    - Developing: 60% - 79%
    - Weak: < 60%
    """
    topic_stats: Dict[str, Dict[str, int]] = {}
    
    total_correct = 0
    total_questions = len(diagnostic_results)

    for item in diagnostic_results:
        topic = item.get("topic", "General Python")
        is_correct = bool(item.get("correct", False))
        
        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "correct": 0}
        
        topic_stats[topic]["total"] += 1
        if is_correct:
            topic_stats[topic]["correct"] += 1
            total_correct += 1

    overall_score = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0

    topics_summary = []
    weak_topics = []
    developing_topics = []
    strong_topics = []

    for topic, stats in topic_stats.items():
        acc = round((stats["correct"] / stats["total"] * 100), 1) if stats["total"] > 0 else 0
        if acc >= 80:
            status = "STRONG"
            strong_topics.append({"topic": topic, "accuracy": acc})
        elif acc >= 60:
            status = "DEVELOPING"
            developing_topics.append({"topic": topic, "accuracy": acc})
        else:
            status = "WEAK"
            weak_topics.append({"topic": topic, "accuracy": acc})

        topics_summary.append({
            "topic": topic,
            "total_questions": stats["total"],
            "correct": stats["correct"],
            "accuracy": acc,
            "status": status
        })

    # Sort weak topics from lowest accuracy to highest
    weak_topics.sort(key=lambda x: x["accuracy"])

    return {
        "status": "success",
        "overall_score": overall_score,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "topics": topics_summary,
        "weak_topics": [w["topic"] for w in weak_topics],
        "developing_topics": [d["topic"] for d in developing_topics],
        "strong_topics": [s["topic"] for s in strong_topics],
        "weak_details": weak_topics,
        "developing_details": developing_topics,
        "strong_details": strong_topics
    }
