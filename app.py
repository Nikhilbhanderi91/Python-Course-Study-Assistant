import os, csv
import streamlit as st
from datetime import datetime

from llm import LLM
from prompts import (
    EXPLANATION_PROMPT, QUIZ_PROMPT, FLASHCARD_PROMPT,
    DIAGNOSTIC_PROMPT, LEARNING_PATH_PROMPT,
    TECHNIQUE_A_PROMPT, TECHNIQUE_B_PROMPT, GUARDRAIL_PROMPT
)
from utils import now, valid_quiz, valid_cards, valid_explanation
import demo
from evaluator import CASES, evaluate

st.set_page_config(page_title="Python Course Study Assistant", page_icon="🐍", layout="wide")

HISTORY = "prompt_history.csv"

def log_history(feature, prompt, result):
    exists = os.path.exists(HISTORY)
    with open(HISTORY, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["timestamp","feature","prompt","result"])
        w.writerow([now(), feature, prompt[:1000], result[:1000]])

def in_scope_simple(topic):
    banned = ["politics","election","movie","song","cricket score","recipe","password"]
    return not any(x in topic.lower() for x in banned)

def get_explanation(topic, difficulty, use_demo):
    if use_demo:
        return demo.explanation(topic,difficulty)
    return LLM().ask_json(EXPLANATION_PROMPT.format(topic=topic,difficulty=difficulty))

def get_quiz(topic, difficulty, n, use_demo):
    if use_demo:
        return demo.quiz(topic,difficulty,n)
    return LLM().ask_json(QUIZ_PROMPT.format(topic=topic,difficulty=difficulty,n=n))

def get_cards(topic, difficulty, n, use_demo):
    if use_demo:
        return demo.cards(topic,difficulty,n)
    return LLM().ask_json(FLASHCARD_PROMPT.format(topic=topic,difficulty=difficulty,n=n))

def get_learning_path(results, use_demo):
    if use_demo:
        return demo.learning_path(results)
    return LLM().ask_json(LEARNING_PATH_PROMPT.format(results=results))

st.title("🐍 Python Course Study Assistant")
st.caption("Hackathon prototype — explain → quiz → flashcards → diagnose → personalized revision")

with st.sidebar:
    st.header("Controls")
    demo_mode = st.toggle("Demo Mode (no API key)", value=not bool(os.getenv("OPENAI_API_KEY","")))
    difficulty = st.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"])
    n = st.slider("Quiz / flashcard items", 3, 10, 5)
    st.info("Scope: Python learning only.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 Learn", "📝 Quiz", "🗂 Flashcards", "🎯 Diagnostic Path", "🧪 Evaluation"
])

with tab1:
    topic = st.text_input("Python topic", placeholder="e.g. lists, functions, OOP, decorators")
    if st.button("Explain", type="primary"):
        if not topic.strip():
            st.error("Please enter a Python topic.")
        elif not in_scope_simple(topic):
            st.warning("Guardrail: please enter a Python-related topic.")
            log_history("guardrail", topic, "blocked")
        else:
            try:
                out = get_explanation(topic,difficulty,demo_mode)
                if not valid_explanation(out):
                    st.error("Guardrail: invalid model output.")
                else:
                    st.subheader(f"{out['topic']} — {out['difficulty']}")
                    st.write(out["explanation"])
                    st.code(out["example"], language="python")
                    st.write("**Common mistake:**", out["common_mistake"])
                    st.write("**Quick check:**", out["check"])
                    log_history("explanation", topic, "success")
            except Exception as e:
                st.error(str(e))

with tab2:
    qtopic = st.text_input("Quiz topic", "Python basics", key="qtopic")
    if st.button("Generate Quiz", type="primary"):
        try:
            out = get_quiz(qtopic,difficulty,n,demo_mode)
            if not valid_quiz(out,n):
                st.error("Guardrail: quiz failed validation.")
            else:
                st.session_state["quiz"] = out
                log_history("quiz", qtopic, "success")
        except Exception as e:
            st.error(str(e))
    if "quiz" in st.session_state:
        score=0
        with st.form("quiz_form"):
            answers=[]
            for i,q in enumerate(st.session_state["quiz"]["questions"]):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                ans=st.radio("Choose",q["options"],key=f"ans_{i}",index=None)
                answers.append(ans)
            submitted=st.form_submit_button("Check Answers")
        if submitted:
            for i,(q,ans) in enumerate(zip(st.session_state["quiz"]["questions"],answers)):
                chosen = ans[0] if ans else ""
                correct = chosen == q["answer"]
                score += int(correct)
                st.write(("✅" if correct else "❌"), f"Q{i+1}: Correct answer = {q['answer']}. {q['explanation']}")
            st.success(f"Score: {score}/{len(answers)} ({score/len(answers)*100:.0f}%)")

with tab3:
    ctopic = st.text_input("Flashcard topic", "Python basics", key="ctopic")
    if st.button("Generate Flashcards", type="primary"):
        try:
            out = get_cards(ctopic,difficulty,n,demo_mode)
            if not valid_cards(out,n):
                st.error("Guardrail: flashcard output failed validation.")
            else:
                st.session_state["cards"] = out
                log_history("flashcards", ctopic, "success")
        except Exception as e:
            st.error(str(e))
    if "cards" in st.session_state:
        for i,c in enumerate(st.session_state["cards"]["cards"],1):
            with st.expander(f"Card {i}: {c['front']}"):
                st.write(c["back"])

with tab4:
    st.write("**Mandatory stretch challenge:** diagnostic quiz → weak-topic analysis → personalized learning path → revision plan.")
    topics = st.text_input("Topics (comma-separated)", "variables, lists, loops, functions, dictionaries")
    if st.button("Start Diagnostic", type="primary"):
        topic_list=[x.strip() for x in topics.split(",") if x.strip()]
        try:
            if demo_mode:
                diag=demo.diagnostic(topic_list,difficulty,5)
            else:
                diag=LLM().ask_json(DIAGNOSTIC_PROMPT.format(topics=", ".join(topic_list),difficulty=difficulty,n=5))
            if not valid_quiz(diag,5):
                st.error("Diagnostic output failed validation.")
            else:
                st.session_state["diag"]=diag
        except Exception as e:
            st.error(str(e))
    if "diag" in st.session_state:
        with st.form("diag_form"):
            answers=[]
            for i,q in enumerate(st.session_state["diag"]["questions"]):
                st.markdown(f"**Q{i+1}. [{q.get('topic','Python')}] {q['question']}**")
                answers.append(st.radio("Answer",q["options"],key=f"dans_{i}",index=None))
            go=st.form_submit_button("Analyze Weak Topics")
        if go:
            results=[]
            for q,ans in zip(st.session_state["diag"]["questions"],answers):
                chosen=ans[0] if ans else ""
                results.append({"topic":q.get("topic","Python"),"correct":chosen==q["answer"]})
            path=get_learning_path(results,demo_mode)
            st.session_state["path"]=path
    if "path" in st.session_state:
        p=st.session_state["path"]
        st.subheader("Diagnostic summary")
        st.write(p["summary"])
        st.write("**Weak topics:**", ", ".join(p["weak_topics"]))
        st.subheader("Personalized learning path")
        for s in p["learning_path"]:
            st.markdown(f"**Step {s['step']}: {s['topic']}** — {s['goal']}  \nActivity: {s['activity']}  \nTime: {s['duration_minutes']} min")
        st.subheader("Revision plan")
        for d in p["revision_plan"]:
            st.markdown(f"**Day {d['day']} — {d['focus']}**")
            for t in d["tasks"]:
                st.write("•",t)

with tab5:
    st.write("### 10+ labelled cases + one metric")
    st.write("Metric: **Valid Item Rate** on expected-valid cases.")
    if st.button("Run Evaluation"):
        def gen(topic,diff,n):
            return get_quiz(topic,diff,n,demo_mode)
        rows,metric=evaluate(gen)
        st.dataframe(rows,use_container_width=True)
        st.metric("Valid Item Rate", f"{metric:.1f}%")
        st.caption("For the final demo, run this once with your first prompt version and save the result, then run after prompt/guardrail improvements.")
    st.write("### Prompting technique comparison")
    c1,c2=st.columns(2)
    compare_topic=st.text_input("Comparison topic","list comprehensions",key="compare")
    if st.button("Compare Techniques"):
        if demo_mode:
            a=f"Technique A (few-shot): {compare_topic} → definition → example → common mistake → check question."
            b=f"Technique B (decomposition + constraints): classify → prerequisite → explanation → valid code → pitfall → self-check."
        else:
            llm=LLM()
            a=llm.ask_text(TECHNIQUE_A_PROMPT.format(topic=compare_topic,difficulty=difficulty))
            b=llm.ask_text(TECHNIQUE_B_PROMPT.format(topic=compare_topic,difficulty=difficulty))
        with c1:
            st.markdown("**Technique A — Few-shot / structured**")
            st.write(a)
        with c2:
            st.markdown("**Technique B — Decomposition + constraints**")
            st.write(b)

st.divider()
st.caption("Prompt history is stored locally in prompt_history.csv with timestamps. Use Git to version prompt files and commits from 11:00 AM onward.")
