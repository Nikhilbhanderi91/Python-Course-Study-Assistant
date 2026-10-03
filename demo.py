"""
Demo fallback mode providing structured, valid mock responses when running offline or testing.
"""

def explanation(topic: str, difficulty: str):
    examples = {
        "lists": ("numbers = [10, 20, 30]\nnumbers.append(40)\nprint(numbers)", "Indexing out of range (IndexError)"),
        "loops": ("for i in range(3):\n    print(f'Count: {i}')", "Infinite while loops without counter updates"),
        "functions": ("def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))", "Forgetting to return a value"),
        "dictionaries": ("student = {'name': 'Alex', 'grade': 'A'}\nprint(student['name'])", "KeyError when accessing missing keys without .get()"),
        "classes": ("class Dog:\n    def __init__(self, name):\n        self.name = name\nd = Dog('Buddy')", "Forgetting 'self' as first method parameter")
    }
    key = topic.lower().strip()
    ex, mist = examples.get(key, (f"# {topic} Example\nval = 10\nprint(f'{topic}: {{val}}')", f"Misunderstanding syntax rules for {topic}"))
    
    return {
        "status": "success",
        "mode": "LEARN",
        "topic": topic,
        "difficulty": difficulty,
        "title": f"Understanding {topic.capitalize()} in Python",
        "definition": f"In Python, {topic} is a foundational concept used to build robust applications.",
        "why_it_is_used": f"It enables developers to structure code, manipulate data, and implement logic efficiently.",
        "syntax": f"# Syntax template for {topic}\n{topic}_construct = ...",
        "example": ex,
        "explanation": f"Line 1 sets up the initial definition or structure. Line 2 uses the feature. Line 3 demonstrates output.",
        "common_mistake": mist,
        "practice_question": f"Write a small script that utilizes {topic} to solve a simple calculation or transformation."
    }

def quiz(topic: str, difficulty: str, n: int = 5):
    bank = [
        {
            "id": 1,
            "question": "Which keyword is used to define a function in Python?",
            "options": ["def", "func", "function", "define"],
            "correct_answer": "def",
            "explanation": "Python uses the 'def' keyword to declare user-defined functions."
        },
        {
            "id": 2,
            "question": "What is the output of `type([1, 2, 3])`?",
            "options": ["<class 'list'>", "<class 'tuple'>", "<class 'set'>", "<class 'dict'>"],
            "correct_answer": "<class 'list'>",
            "explanation": "Square brackets denote a list object in Python."
        },
        {
            "id": 3,
            "question": "Which data structure stores unique elements with no duplicates?",
            "options": ["set", "list", "tuple", "dict"],
            "correct_answer": "set",
            "explanation": "Sets only contain unique elements and automatically discard duplicates."
        },
        {
            "id": 4,
            "question": "What is the correct way to handle exceptions in Python?",
            "options": ["try / except", "try / catch", "do / rescue", "begin / error"],
            "correct_answer": "try / except",
            "explanation": "Python utilizes 'try' and 'except' blocks for exception handling."
        },
        {
            "id": 5,
            "question": "What does the expression `10 // 3` evaluate to in Python?",
            "options": ["3", "3.33", "3.0", "1"],
            "correct_answer": "3",
            "explanation": "'//' performs integer floor division, returning 3."
        },
        {
            "id": 6,
            "question": "Which built-in function returns the number of items in a collection?",
            "options": ["len()", "count()", "size()", "length()"],
            "correct_answer": "len()",
            "explanation": "len() returns the length of sequences and collections."
        },
        {
            "id": 7,
            "question": "Which statement correctly creates an empty dictionary?",
            "options": ["{}", "[]", "set()", "()"],
            "correct_answer": "{}",
            "explanation": "{} creates an empty dictionary in Python."
        },
        {
            "id": 8,
            "question": "How do you access the first element in `my_list = [10, 20, 30]`?",
            "options": ["my_list[0]", "my_list[1]", "my_list.first()", "my_list(0)"],
            "correct_answer": "my_list[0]",
            "explanation": "Python indexing is 0-based."
        },
        {
            "id": 9,
            "question": "Which method adds a single element to the end of a list?",
            "options": ["append()", "extend()", "insert()", "add()"],
            "correct_answer": "append()",
            "explanation": "append() appends an element to the end of an existing list."
        },
        {
            "id": 10,
            "question": "What is the purpose of the `__init__` method in Python classes?",
            "options": ["Object constructor / initializer", "Destructor", "Import module", "Declare static method"],
            "correct_answer": "Object constructor / initializer",
            "explanation": "__init__ is called when a new instance of a class is created."
        }
    ]
    return {
        "status": "success",
        "mode": "QUIZ",
        "topic": topic,
        "difficulty": difficulty,
        "questions": bank[:n]
    }

def flashcards(topic: str, difficulty: str, n: int = 5):
    cards = [
        {
            "id": 1,
            "front": f"What is the primary purpose of {topic}?",
            "back": f"Enables structured problem-solving and clean logic flow in Python.",
            "example": f"# {topic} usage\npass"
        },
        {
            "id": 2,
            "front": "What keyword or syntax is central to this concept?",
            "back": "Refer to the standard library Python documentation for exact keyword semantics.",
            "example": "x = 42"
        },
        {
            "id": 3,
            "front": "What is a common error or bug encountered here?",
            "back": "Type mismatch, index out of bounds, or incorrect indentation.",
            "example": "# Error avoidance\ntry:\n    ...\nexcept Exception:\n    pass"
        },
        {
            "id": 4,
            "front": "How do you inspect the methods available for an object?",
            "back": "Use the dir() and help() built-in introspection functions.",
            "example": "dir(str)"
        },
        {
            "id": 5,
            "front": "What is the time complexity consideration?",
            "back": "Dictionaries and sets offer O(1) average lookup; lists offer O(n) search.",
            "example": "val in {'a': 1}"
        }
    ]
    return {
        "status": "success",
        "mode": "FLASHCARDS",
        "topic": topic,
        "difficulty": difficulty,
        "flashcards": cards[:n]
    }

def diagnostic():
    return {
        "status": "success",
        "mode": "DIAGNOSTIC",
        "questions": [
            {
                "id": 1,
                "topic": "Variables & Data Types",
                "question": "What is the data type of the result of `10 / 2` in Python 3?",
                "options": ["float", "int", "decimal", "double"],
                "correct_answer": "float",
                "explanation": "The standard division operator `/` always produces a float in Python 3."
            },
            {
                "id": 2,
                "topic": "Conditions & Logic",
                "question": "What does `bool([])` evaluate to in Python?",
                "options": ["False", "True", "None", "TypeError"],
                "correct_answer": "False",
                "explanation": "Empty sequences (lists, strings, tuples) evaluate to False in boolean context."
            },
            {
                "id": 3,
                "topic": "Loops",
                "question": "Which keyword immediately exits the current enclosing loop?",
                "options": ["break", "continue", "pass", "exit"],
                "correct_answer": "break",
                "explanation": "`break` terminates the nearest enclosing loop."
            },
            {
                "id": 4,
                "topic": "Functions & Scope",
                "question": "What keyword allows modifying a variable outside the local function scope?",
                "options": ["global", "nonlocal", "extern", "outer"],
                "correct_answer": "global",
                "explanation": "`global` declares that a variable inside a function refers to the module-level scope."
            },
            {
                "id": 5,
                "topic": "Lists & Tuples",
                "question": "What is the key difference between a list and a tuple?",
                "options": ["Lists are mutable, tuples are immutable", "Tuples can only store numbers", "Lists cannot be sliced", "Tuples cannot be indexed"],
                "correct_answer": "Lists are mutable, tuples are immutable",
                "explanation": "Tuples cannot be modified after creation, while lists can be mutated in-place."
            },
            {
                "id": 6,
                "topic": "Dictionaries & Sets",
                "question": "What method safely retrieves a dictionary value without raising a KeyError?",
                "options": [".get()", ".find()", ".lookup()", ".fetch()"],
                "correct_answer": ".get()",
                "explanation": "`.get(key, default)` returns None or a default if the key is missing."
            },
            {
                "id": 7,
                "topic": "Exception Handling",
                "question": "Which block always runs regardless of whether an exception occurred?",
                "options": ["finally", "else", "except", "always"],
                "correct_answer": "finally",
                "explanation": "The `finally` block is guaranteed to execute for cleanup."
            },
            {
                "id": 8,
                "topic": "Object-Oriented Programming",
                "question": "What does `self` represent inside an instance method?",
                "options": ["The instance of the class", "The class object itself", "The parent class", "A reserved global keyword"],
                "correct_answer": "The instance of the class",
                "explanation": "`self` represents the specific object instance being operated on."
            },
            {
                "id": 9,
                "topic": "List Comprehensions",
                "question": "What is the output of `[x * 2 for x in range(3)]`?",
                "options": ["[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "[2, 4]"],
                "correct_answer": "[0, 2, 4]",
                "explanation": "`range(3)` produces 0, 1, 2. Multiplying each by 2 yields [0, 2, 4]."
            },
            {
                "id": 10,
                "topic": "Problem Solving & Debugging",
                "question": "What built-in function pauses execution to launch the interactive debugger?",
                "options": ["breakpoint()", "debug()", "pause()", "stop()"],
                "correct_answer": "breakpoint()",
                "explanation": "`breakpoint()` drops the program into `pdb` in Python 3.7+."
            }
        ]
    }

def learning_path(perf: dict):
    weak = perf.get("weak_topics", ["Functions & Scope"])
    weak_details = perf.get("weak_details", [{"topic": "Functions & Scope", "accuracy": 40.0}])
    
    plan_weak = []
    for w in weak_details:
        t = w["topic"]
        acc = w["accuracy"]
        plan_weak.append({
            "topic": t,
            "accuracy": acc,
            "reason": f"Demonstrated {acc}% accuracy on diagnostic questions for {t}.",
            "learning_objectives": [
                f"Master fundamentals and core mechanics of {t}.",
                f"Avoid common syntax traps and solve practice drills for {t}."
            ],
            "revision_steps": [
                f"Review {t} definition, basic syntax, and mental models.",
                f"Write 3 hands-on Python scripts utilizing {t}."
            ],
            "practice_activity": f"Build a mini project module applying {t}.",
            "retest": f"Target >= 80% on 5-question {t} retest."
        })

    primary_weak = weak[0] if weak else "Core Python Fundamentals"
    secondary_weak = weak[1] if len(weak) > 1 else primary_weak

    return {
        "status": "success",
        "weak_topics": plan_weak,
        "personalized_plan": [
            {
                "day": 1,
                "topic": f"Deep Dive: {primary_weak}",
                "activities": [
                    f"Study foundational concepts of {primary_weak}",
                    "Code 3 minimal working examples",
                    "Complete 3-question mini quiz (Target: 100%)"
                ]
            },
            {
                "day": 2,
                "topic": f"Application & Edge Cases: {primary_weak}",
                "activities": [
                    "Explore pitfalls and error handling",
                    "Refactor previous code to use best practices",
                    "Complete 3-question mini quiz"
                ]
            },
            {
                "day": 3,
                "topic": f"Targeted Study: {secondary_weak}",
                "activities": [
                    f"Review prerequisites and core rules of {secondary_weak}",
                    "Write interactive test cases",
                    "Complete 3-question mini quiz"
                ]
            },
            {
                "day": 4,
                "topic": "Mixed Review & Retest",
                "activities": [
                    "Mixed topic coding challenges",
                    "Full diagnostic retest benchmark",
                    "Verify mastery target (>= 80% accuracy)"
                ]
            }
        ]
    }
