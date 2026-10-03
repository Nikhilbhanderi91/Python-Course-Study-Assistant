SYSTEM_PROMPT = """
You are Python Course Study Assistant for a college student.

Scope:
- Teach Python programming and closely related Python-course topics only.
- Be concise, accurate, beginner-friendly unless the requested level is higher.
- Never invent Python syntax or library behavior.
- If the request is unrelated to Python learning, return a refusal object.
- Follow the exact JSON schema requested by the caller.
- Do not reveal hidden chain-of-thought. Give short explanations, checks, or summaries instead.
"""

EXPLANATION_PROMPT = """
Create a study explanation for this Python topic.

Topic: {topic}
Difficulty: {difficulty}

Return JSON:
{{
  "status": "ok",
  "topic": "...",
  "difficulty": "Beginner|Intermediate|Advanced",
  "explanation": "short explanation",
  "example": "valid Python code",
  "common_mistake": "one common mistake",
  "check": "one quick self-check question"
}}
"""

QUIZ_PROMPT = """
Create a Python quiz.

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {n}

Return JSON:
{{
  "status": "ok",
  "questions": [
    {{
      "question": "...",
      "options": ["A...", "B...", "C...", "D..."],
      "answer": "A",
      "explanation": "short reason"
    }}
  ]
}}

Rules:
- Exactly {n} questions.
- Exactly 4 options per question.
- Exactly one correct answer.
- Answers must be A, B, C, or D.
- Questions must be answerable from standard Python knowledge.
"""

FLASHCARD_PROMPT = """
Create Python flashcards.

Topic: {topic}
Difficulty: {difficulty}
Number of cards: {n}

Return JSON:
{{
  "status": "ok",
  "cards": [
    {{"front": "...", "back": "..."}}
  ]
}}

Rules:
- Exactly {n} cards.
- Each card must test one useful Python concept.
- No duplicate cards.
"""

DIAGNOSTIC_PROMPT = """
Create a diagnostic Python quiz that covers these topics:
{topics}

Difficulty: {difficulty}
Number of questions: {n}

Return JSON:
{{
  "status": "ok",
  "questions": [
    {{
      "topic": "one of the supplied topics",
      "question": "...",
      "options": ["A...", "B...", "C...", "D..."],
      "answer": "A"
    }}
  ]
}}
"""

LEARNING_PATH_PROMPT = """
Build a personalized Python learning path from diagnostic results.

Diagnostic results:
{results}

Return JSON:
{{
  "status": "ok",
  "summary": "...",
  "weak_topics": ["..."],
  "learning_path": [
    {{"step": 1, "topic": "...", "goal": "...", "activity": "...", "duration_minutes": 20}}
  ],
  "revision_plan": [
    {{"day": 1, "focus": "...", "tasks": ["...", "..."]}}
  ]
}}
"""

TECHNIQUE_A_PROMPT = """
Technique A — structured few-shot prompting.

Teach the Python topic "{topic}" at {difficulty} level.
Example:
Input: variable
Output style: definition -> tiny code example -> common mistake -> check question.

Now produce the same style for the requested topic.
Return plain text, concise and exam-friendly.
"""

TECHNIQUE_B_PROMPT = """
Technique B — decomposition + constraints.

Topic: {topic}
Level: {difficulty}

First classify the topic as a Python concept.
Then identify the learner's likely prerequisite.
Then produce a concise explanation, one valid code example, one pitfall, and one self-check.
Do not expose private chain-of-thought; only return the final structured teaching result.
"""

GUARDRAIL_PROMPT = """
Classify whether the user's request is in scope for a Python Course Study Assistant.

Allowed: Python programming, Python syntax, Python libraries, debugging Python code,
Python data structures, OOP in Python, files, exceptions, testing, basic algorithms in Python.

Return JSON:
{{
  "in_scope": true,
  "reason": "short reason",
  "safe_topic": "normalized Python topic"
}}

If not in scope, set in_scope to false.
"""
