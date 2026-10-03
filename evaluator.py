"""
Evaluation test suite for Python Course Study Assistant.
Measures Format Validity Rate across labelled test cases.
"""

from utils import (
    validate_input,
    validate_learn_output,
    validate_quiz_output,
    validate_flashcards_output,
    validate_diagnostic_output
)

CASES = [
    {"id": "E01", "category": "Normal Python topic", "mode": "LEARN", "topic": "Lists", "difficulty": "Beginner", "expected_status": "success"},
    {"id": "E02", "category": "Beginner topic", "mode": "LEARN", "topic": "Variables and Data Types", "difficulty": "Beginner", "expected_status": "success"},
    {"id": "E03", "category": "Intermediate topic", "mode": "LEARN", "topic": "Exception Handling", "difficulty": "Intermediate", "expected_status": "success"},
    {"id": "E04", "category": "Advanced topic", "mode": "LEARN", "topic": "Decorators and Generators", "difficulty": "Advanced", "expected_status": "success"},
    {"id": "E05", "category": "Quiz generation", "mode": "QUIZ", "topic": "Python Functions", "difficulty": "Intermediate", "expected_status": "success"},
    {"id": "E06", "category": "Flashcard generation", "mode": "FLASHCARDS", "topic": "Dictionaries", "difficulty": "Beginner", "expected_status": "success"},
    {"id": "E07", "category": "Diagnostic input", "mode": "DIAGNOSTIC", "topic": "Python Comprehensive", "difficulty": "Intermediate", "expected_status": "success"},
    {"id": "E08", "category": "Empty input", "mode": "LEARN", "topic": "", "difficulty": "Beginner", "expected_status": "rejected"},
    {"id": "E09", "category": "Off-topic input", "mode": "LEARN", "topic": "What is the weather in Paris today?", "difficulty": "Beginner", "expected_status": "rejected"},
    {"id": "E10", "category": "Invalid difficulty input", "mode": "LEARN", "topic": "Loops", "difficulty": "SuperHard", "expected_status": "rejected"},
    {"id": "E11", "category": "Unusual Python topic", "mode": "LEARN", "topic": "Context Managers with `__enter__` and `__exit__`", "difficulty": "Advanced", "expected_status": "success"},
    {"id": "E12", "category": "Excessively long input", "mode": "LEARN", "topic": "Python " * 100, "difficulty": "Beginner", "expected_status": "rejected"}
]

def evaluate(pipeline_fn):
    """
    Evaluates pipeline across all test cases.
    Formula: Format Validity Rate = Valid Outputs / Total Test Cases * 100
    """
    rows = []
    valid_count = 0
    total_count = len(CASES)

    for case in CASES:
        case_id = case["id"]
        category = case["category"]
        mode = case["mode"]
        topic = case["topic"]
        difficulty = case["difficulty"]
        expected_status = case["expected_status"]

        # Run input guardrail first
        is_valid_input, guardrail_error = validate_input(topic, mode, difficulty)

        if not is_valid_input:
            actual_status = guardrail_error.get("status", "rejected")
            passed = (actual_status == expected_status)
            result_detail = guardrail_error.get("reason", "GUARDRAIL_BLOCKED")
        else:
            try:
                out = pipeline_fn(topic, mode, difficulty)
                actual_status = out.get("status", "error")

                if mode == "LEARN":
                    schema_ok = validate_learn_output(out)
                elif mode == "QUIZ":
                    schema_ok = validate_quiz_output(out, expected_count=5)
                elif mode == "FLASHCARDS":
                    schema_ok = validate_flashcards_output(out, expected_count=5)
                elif mode == "DIAGNOSTIC":
                    schema_ok = validate_diagnostic_output(out)
                else:
                    schema_ok = False

                passed = (actual_status == expected_status) and schema_ok
                result_detail = "VALID_SCHEMA" if schema_ok else "INVALID_SCHEMA"
            except Exception as e:
                passed = False
                result_detail = f"EXCEPTION: {str(e)[:40]}"

        if passed:
            valid_count += 1

        rows.append({
            "ID": case_id,
            "Category": category,
            "Mode": mode,
            "Topic": topic[:30] + ("..." if len(topic) > 30 else ""),
            "Expected": expected_status,
            "Status": "PASS" if passed else "FAIL",
            "Detail": result_detail
        })

    metric = (valid_count / total_count * 100) if total_count > 0 else 0
    return rows, metric
