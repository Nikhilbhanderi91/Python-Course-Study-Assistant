import csv, os
from datetime import datetime

CASES = [
    ("E01","valid","lists","Beginner"),
    ("E02","valid","functions","Beginner"),
    ("E03","valid","loops","Intermediate"),
    ("E04","valid","dictionaries","Beginner"),
    ("E05","valid","exceptions","Intermediate"),
    ("E06","valid","classes","Advanced"),
    ("E07","invalid","asdfghjkl","Beginner"),
    ("E08","off_topic","write a political speech","Intermediate"),
    ("E09","valid","list comprehensions","Advanced"),
    ("E10","valid","file handling","Intermediate"),
    ("E11","valid","lambda functions","Advanced"),
    ("E12","valid","sets","Beginner"),
]

def evaluate(generator):
    rows=[]
    valid=0
    total=0
    for case_id, label, topic, difficulty in CASES:
        try:
            result = generator(topic, difficulty, 5)
            ok = isinstance(result, dict) and result.get("status") == "ok" and len(result.get("questions",[])) == 5
        except Exception:
            ok=False
        expected = label=="valid"
        passed = ok == expected
        rows.append({"case":case_id,"label":label,"topic":topic,"result":"PASS" if passed else "FAIL"})
        if label=="valid":
            total += 1
            valid += int(ok)
    metric = (valid/total*100) if total else 0
    return rows, metric
