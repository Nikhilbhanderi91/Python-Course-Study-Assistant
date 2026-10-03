def explanation(topic, difficulty):
    examples = {
        "lists": "numbers = [10, 20, 30]\nprint(numbers[0])",
        "loops": "for i in range(3):\n    print(i)",
        "functions": "def add(a, b):\n    return a + b",
        "dictionaries": "student = {'name': 'Asha', 'age': 20}\nprint(student['name'])",
        "oops": "class Student:\n    def __init__(self, name):\n        self.name = name"
    }
    key = topic.lower()
    ex = examples.get(key, f"# Example for {topic}\\nprint('Learn {topic} in Python')")
    return {
        "status":"ok","topic":topic,"difficulty":difficulty,
        "explanation":f"{topic} is a Python concept. At {difficulty} level, learn the core idea, syntax, and a small example.",
        "example":ex,
        "common_mistake":f"Using {topic} without checking the correct Python syntax or data type.",
        "check":f"Can you explain {topic} in one sentence and write a small example?"
    }

def quiz(topic, difficulty, n):
    bank = [
        {"question":"Which symbol starts a comment in Python?","options":["A. //","B. #","C. <!--","D. **"],"answer":"B","explanation":"Python uses # for single-line comments."},
        {"question":"What is the type of [1, 2, 3]?","options":["A. tuple","B. set","C. list","D. dict"],"answer":"C","explanation":"Square brackets create a list."},
        {"question":"Which keyword defines a function?","options":["A. func","B. define","C. function","D. def"],"answer":"D","explanation":"Python functions are defined with def."},
        {"question":"What does len('Python') return?","options":["A. 5","B. 6","C. 7","D. Error"],"answer":"B","explanation":"Python has 6 letters."},
        {"question":"Which data type stores key-value pairs?","options":["A. list","B. tuple","C. dict","D. str"],"answer":"C","explanation":"Dictionaries store key-value pairs."},
        {"question":"What is 3 // 2?","options":["A. 1","B. 1.5","C. 2","D. 0"],"answer":"A","explanation":"// is floor division."},
        {"question":"Which value is Boolean?","options":["A. 'True'","B. 1","C. True","D. true"],"answer":"C","explanation":"True is Python's Boolean literal."},
        {"question":"Which statement repeats over a sequence?","options":["A. for","B. import","C. pass","D. with"],"answer":"A","explanation":"for iterates over items in a sequence/iterable."},
        {"question":"What does append() do to a list?","options":["A. Removes an item","B. Adds an item at the end","C. Sorts the list","D. Copies the list"],"answer":"B","explanation":"append adds one item to the end."},
        {"question":"Which block handles an exception?","options":["A. if/else","B. for/in","C. try/except","D. with/as"],"answer":"C","explanation":"try/except is used for exception handling."}
    ]
    return {"status":"ok","questions":bank[:n]}

def cards(topic, difficulty, n):
    base = [
        ("What keyword defines a function?","def"),
        ("What collection stores key-value pairs?","Dictionary (dict)"),
        ("What does len() return?","The number of items/characters."),
        ("What does append() do?","Adds an item to the end of a list."),
        ("What symbol starts a Python comment?","#"),
        ("What is floor division?","Division using // that returns the floor of the quotient.")
    ]
    return {"status":"ok","cards":[{"front":f"{q} ({topic})","back":a} for q,a in base[:n]]}

def diagnostic(topics, difficulty, n):
    qs = quiz("Python basics", difficulty, n)["questions"]
    for i,q in enumerate(qs):
        q["topic"] = topics[i % len(topics)]
    return {"status":"ok","questions":qs}

def learning_path(results):
    weak = [r["topic"] for r in results if not r["correct"]]
    if not weak:
        weak = ["Advanced practice"]
    return {
        "status":"ok",
        "summary":"Your incorrect diagnostic answers identify the topics that should receive extra revision time.",
        "weak_topics":weak,
        "learning_path":[
            {"step":i+1,"topic":t,"goal":f"Understand {t} and write 2 small examples.","activity":"Study the explanation, solve 3 practice questions, then explain the concept aloud.","duration_minutes":20}
            for i,t in enumerate(dict.fromkeys(weak))
        ],
        "revision_plan":[
            {"day":1,"focus":weak[0],"tasks":["Review notes","Solve 5 easy questions"]},
            {"day":2,"focus":weak[min(1,len(weak)-1)],"tasks":["Write 2 programs","Take a mini quiz"]},
            {"day":3,"focus":"Mixed revision","tasks":["Retake diagnostic","Review mistakes"]}
        ]
    }
