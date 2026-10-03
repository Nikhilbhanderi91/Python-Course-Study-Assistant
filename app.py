import os
import csv
import streamlit as st

from llm import LLM
from prompts import (
    LEARN_PROMPT,
    QUIZ_PROMPT,
    FLASHCARD_PROMPT,
    DIAGNOSTIC_PROMPT,
    LEARNING_PATH_PROMPT,
    TECHNIQUE_A_PROMPT,
    TECHNIQUE_B_PROMPT
)
from utils import (
    now,
    validate_input,
    validate_learn_output,
    validate_quiz_output,
    validate_flashcards_output,
    validate_diagnostic_output,
    calculate_performance
)
import demo
from evaluator import evaluate

st.set_page_config(page_title="Python Course Study Assistant", page_icon="🐍", layout="wide")

HISTORY_FILE = "prompt_history.csv"

def log_history(version: str, change_description: str, problem_or_reason: str, observed_result: str):
    exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "prompt_version", "change_made", "problem_or_reason", "observed_result"])
        writer.writerow([now(), version, change_description, problem_or_reason, observed_result])

def call_gemini_json(prompt: str, demo_mode: bool, fallback_fn):
    if demo_mode:
        return fallback_fn()
    llm = LLM()
    if not llm.available:
        return fallback_fn()
    return llm.generate_json(prompt)

# Sidebar
with st.sidebar:
    st.header("⚙️ Assistant Controls")
    has_api_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
    demo_mode = st.toggle("Demo Mode (Offline / Mock)", value=not has_api_key)
    
    if not has_api_key and not demo_mode:
        st.warning("⚠️ No GEMINI_API_KEY found in .env. Switched to Demo Mode.")
        demo_mode = True

    difficulty = st.selectbox("Select Difficulty", ["Beginner", "Intermediate", "Advanced"], index=0)
    st.markdown("---")
    st.info("🎯 **Scope**: Exclusively Python Programming & Computer Science concepts.")
    st.caption("Powered by Google Gemini 2.5 Flash")

st.title("🐍 Python Course Study Assistant")
st.caption("Adaptive Learning • Diagnostic Assessment • Weak Topic Analysis • Personalized Revision Plan")

tab_learn, tab_quiz, tab_flashcards, tab_diagnostic, tab_eval = st.tabs([
    "📚 Learn Mode",
    "📝 Quiz Mode",
    "🗂 Flashcard Mode",
    "🎯 Diagnostic & Learning Path",
    "🧪 Evaluation & Prompt Engineering"
])

# -----------------------------------------------------------------------------
# 1. LEARN MODE
# -----------------------------------------------------------------------------
with tab_learn:
    st.subheader("Explain & Master Python Concepts")
    topic_input = st.text_input(
        "Enter Python Topic:",
        value=st.session_state.get("current_topic", ""),
        placeholder="e.g. Lists, Dictionaries, Functions, Decorators, Try/Except",
        key="learn_topic"
    )
    
    if st.button("📖 Generate Explanation, Quiz & Flashcards", type="primary", key="btn_learn"):
        is_valid, err = validate_input(topic_input, "LEARN", difficulty)
        if not is_valid:
            st.error(f"🛑 **{err.get('reason')}**: {err.get('message')}")
            log_history("V4", f"Learn input for '{topic_input}'", "Input validation rejected", err.get("reason"))
        else:
            clean_topic = topic_input.strip()
            st.session_state["current_topic"] = clean_topic
            seed_val = now()
            
            with st.spinner(f"Generating explanation, fresh quiz, and flashcards for '{clean_topic}'..."):
                # 1. Generate explanation
                learn_prompt = LEARN_PROMPT.format(topic=clean_topic, difficulty=difficulty)
                learn_res = call_gemini_json(learn_prompt, demo_mode, lambda: demo.explanation(clean_topic, difficulty))
                
                # 2. Automatically generate matching 5-question quiz with fresh seed
                quiz_prompt = QUIZ_PROMPT.format(topic=clean_topic, difficulty=difficulty, seed=seed_val)
                quiz_res = call_gemini_json(quiz_prompt, demo_mode, lambda: demo.quiz(clean_topic, difficulty, 5))
                
                # 3. Automatically generate matching 5-card flashcard set with fresh seed
                flashcard_prompt = FLASHCARD_PROMPT.format(topic=clean_topic, difficulty=difficulty, seed=seed_val)
                flashcard_res = call_gemini_json(flashcard_prompt, demo_mode, lambda: demo.flashcards(clean_topic, difficulty, 5))
                
                if validate_learn_output(learn_res):
                    st.session_state["learn_res"] = learn_res
                    log_history("FINAL", f"Learn explanation for {clean_topic}", "Standard learn request", "SUCCESS")
                else:
                    st.error("⚠️ Explanation output validation failed schema check.")
                
                if validate_quiz_output(quiz_res, 5):
                    st.session_state["active_quiz"] = quiz_res
                    st.session_state["quiz_submitted"] = False
                    log_history("FINAL", f"Auto quiz generation for {clean_topic}", "Generated matching quiz", "SUCCESS")
                
                if validate_flashcards_output(flashcard_res, 5):
                    st.session_state["active_cards"] = flashcard_res
                    log_history("FINAL", f"Auto flashcards for {clean_topic}", "Generated 5 cards", "SUCCESS")

    if "learn_res" in st.session_state:
        res = st.session_state["learn_res"]
        st.success(f"### {res['title']} ({res['difficulty']} Level)")
        st.markdown(f"**📖 Definition:**\n{res['definition']}")
        st.markdown(f"**💡 Why it is used:**\n{res['why_it_is_used']}")
        
        st.markdown("**💻 Syntax & Example:**")
        st.code(res["example"], language="python")
        
        st.markdown(f"**🔍 Line-by-Line / Detailed Explanation:**\n{res['explanation']}")
        
        st.warning(f"⚠️ **Common Beginner/Learner Mistake:**\n{res['common_mistake']}")
        st.info(f"✍️ **Practice Challenge:**\n{res['practice_question']}")
        st.info("✨ **5-Question Quiz** and **Active-Recall Flashcards** have been created for this exact topic! Check the **📝 Quiz Mode** and **🗂 Flashcard Mode** tabs.")

# -----------------------------------------------------------------------------
# 2. QUIZ MODE
# -----------------------------------------------------------------------------
with tab_quiz:
    st.subheader("📝 Multiple-Choice Knowledge Check (5 Questions)")
    current_topic = st.session_state.get("current_topic", "")
    
    if not current_topic:
        st.info("👉 Enter a topic in the **📚 Learn Mode** tab to study and auto-generate your quiz here.")
    else:
        st.markdown(f"Current Topic: **{current_topic}** ({difficulty} Level)")
        
        if st.button("🔄 Generate Fresh Questions for this Topic", key="btn_refresh_quiz"):
            seed_val = now()
            with st.spinner(f"Generating 5 new, unique questions for '{current_topic}'..."):
                prompt = QUIZ_PROMPT.format(topic=current_topic, difficulty=difficulty, seed=seed_val)
                res = call_gemini_json(prompt, demo_mode, lambda: demo.quiz(current_topic, difficulty, 5))
                if validate_quiz_output(res, 5):
                    st.session_state["active_quiz"] = res
                    st.session_state["quiz_submitted"] = False
                    log_history("FINAL", f"Refreshed quiz for {current_topic}", "Generated 5 new questions", "SUCCESS")

    if "active_quiz" in st.session_state and current_topic:
        quiz_data = st.session_state["active_quiz"]
        st.markdown(f"#### Quiz on: **{quiz_data['topic']}** ({quiz_data['difficulty']})")
        
        with st.form("quiz_form"):
            user_answers = []
            for i, q in enumerate(quiz_data["questions"]):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                ans = st.radio(
                    f"Select answer for Question {i+1}:",
                    options=q["options"],
                    key=f"q_radio_{q['id']}_{i}_{quiz_data.get('topic')}",
                    index=None
                )
                user_answers.append(ans)
            
            submit_quiz = st.form_submit_button("Submit & Grade Quiz")
            
        if submit_quiz:
            score = 0
            total = len(quiz_data["questions"])
            st.markdown("---")
            st.subheader("Quiz Results & Detailed Feedback")
            
            for i, (q, chosen) in enumerate(zip(quiz_data["questions"], user_answers)):
                is_correct = (chosen == q["correct_answer"])
                if is_correct:
                    score += 1
                    st.success(f"✅ **Q{i+1}: Correct!**\n\nYour Answer: `{chosen}`\n\n*Explanation:* {q['explanation']}")
                else:
                    st.error(f"❌ **Q{i+1}: Incorrect.**\n\nYour Answer: `{chosen if chosen else 'None'}`\n\nCorrect Answer: `{q['correct_answer']}`\n\n*Explanation:* {q['explanation']}")
            
            accuracy = round((score / total * 100), 1)
            st.metric("Total Score", f"{score} / {total}", f"{accuracy}% Accuracy")
            
            # Adaptive learning recommendation
            if accuracy >= 80:
                st.balloons()
                st.success("🌟 **Strong Performance!** You have demonstrated solid grasp of this concept. Ready for more advanced topics or challenges.")
            elif accuracy >= 60:
                st.warning("📈 **Developing Knowledge!** Good foundation, but review the explanations above and target the practice problems.")
            else:
                st.error("🚨 **Weak Performance!** Recommend revisiting the Learn module for this topic and attempting the practice activities.")

# -----------------------------------------------------------------------------
# 3. FLASHCARDS MODE
# -----------------------------------------------------------------------------
with tab_flashcards:
    st.subheader("🗂 Active-Recall Flashcards (5 Cards)")
    current_topic = st.session_state.get("current_topic", "")
    
    if not current_topic:
        st.info("👉 Enter a topic in the **📚 Learn Mode** tab to study and auto-generate your flashcards here.")
    else:
        st.markdown(f"Current Topic: **{current_topic}** ({difficulty} Level)")
        
        if st.button("🔄 Generate Fresh Flashcards for this Topic", key="btn_refresh_cards"):
            seed_val = now()
            with st.spinner(f"Generating 5 new flashcards for '{current_topic}'..."):
                prompt = FLASHCARD_PROMPT.format(topic=current_topic, difficulty=difficulty, seed=seed_val)
                res = call_gemini_json(prompt, demo_mode, lambda: demo.flashcards(current_topic, difficulty, 5))
                if validate_flashcards_output(res, 5):
                    st.session_state["active_cards"] = res
                    log_history("FINAL", f"Refreshed flashcards for {current_topic}", "Generated 5 new cards", "SUCCESS")

    if "active_cards" in st.session_state and current_topic:
        cards_data = st.session_state["active_cards"]
        st.markdown(f"#### Flashcards: **{cards_data['topic']}**")
        for i, card in enumerate(cards_data["flashcards"], 1):
            with st.expander(f"🗂️ Card {i}: {card['front']}", expanded=(i==1)):
                st.markdown(f"**Answer / Concept:**\n{card['back']}")
                if card.get("example"):
                    st.code(card["example"], language="python")

# -----------------------------------------------------------------------------
# 4. DIAGNOSTIC & PERSONALIZED LEARNING PATH (MANDATORY STRETCH CHALLENGE)
# -----------------------------------------------------------------------------
with tab_diagnostic:
    st.subheader("🎯 Diagnostic Knowledge Assessment & Personalized Revision Plan")
    st.write("Take a 10-question diagnostic covering core Python domains to identify your weaknesses and generate a personalized 4-session revision plan.")
    
    if st.button("Start 10-Question Diagnostic Quiz", type="primary", key="btn_start_diag"):
        with st.spinner("Synthesizing 10-question comprehensive diagnostic quiz..."):
            res = call_gemini_json(DIAGNOSTIC_PROMPT, demo_mode, lambda: demo.diagnostic())
            if not validate_diagnostic_output(res):
                st.error("⚠️ Diagnostic quiz failed schema check.")
            else:
                st.session_state["diagnostic_quiz"] = res
                st.session_state.pop("learning_path_result", None)

    if "diagnostic_quiz" in st.session_state:
        diag = st.session_state["diagnostic_quiz"]
        
        with st.form("diagnostic_form"):
            st.markdown("### Answer all 10 Diagnostic Questions:")
            d_answers = []
            for i, q in enumerate(diag["questions"]):
                st.markdown(f"**Q{i+1} [{q['topic']}]:** {q['question']}")
                d_ans = st.radio(
                    f"Answer for Q{i+1}:",
                    options=q["options"],
                    key=f"diag_q_{i}",
                    index=None
                )
                d_answers.append(d_ans)
            
            submit_diag = st.form_submit_button("Analyze Weak Topics & Generate Learning Path")
            
        if submit_diag:
            # 1. Calculate genuine performance metrics
            eval_results = []
            for q, chosen in zip(diag["questions"], d_answers):
                is_correct = (chosen == q["correct_answer"])
                eval_results.append({
                    "topic": q["topic"],
                    "question": q["question"],
                    "chosen": chosen,
                    "correct_answer": q["correct_answer"],
                    "correct": is_correct
                })
            
            perf = calculate_performance(eval_results)
            st.session_state["diag_perf"] = perf
            
            # 2. Prompt Chaining: Generate Personalized Learning Path & 4-Session Revision Plan
            with st.spinner("Analyzing weak topics and building personalized 4-session revision path..."):
                perf_summary_str = f"Overall Accuracy: {perf['overall_score']}%, Total Correct: {perf['total_correct']}/{perf['total_questions']}"
                prompt_lp = LEARNING_PATH_PROMPT.format(
                    performance_summary=perf_summary_str,
                    weak_topics=", ".join(perf["weak_topics"]) if perf["weak_topics"] else "None",
                    developing_topics=", ".join(perf["developing_topics"]) if perf["developing_topics"] else "None",
                    strong_topics=", ".join(perf["strong_topics"]) if perf["strong_topics"] else "None"
                )
                
                path_res = call_gemini_json(prompt_lp, demo_mode, lambda: demo.learning_path(perf))
                st.session_state["learning_path_result"] = path_res

    if "diag_perf" in st.session_state and "learning_path_result" in st.session_state:
        perf = st.session_state["diag_perf"]
        plan = st.session_state["learning_path_result"]
        
        st.markdown("---")
        st.subheader("📊 Diagnostic Performance Analysis")
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", f"{perf['overall_score']}%", f"{perf['total_correct']}/{perf['total_questions']} Correct")
        col2.metric("Weak Topics (< 60%)", f"{len(perf['weak_topics'])} Areas", delta_color="inverse")
        col3.metric("Strong Topics (>= 80%)", f"{len(perf['strong_topics'])} Areas")
        
        # Topic breakdown table
        st.markdown("#### Topic-by-Topic Breakdown")
        st.dataframe(perf["topics"], use_container_width=True)
        
        # Personalized Learning Path
        st.markdown("---")
        st.subheader("🗺️ Personalized Learning Path for Weak Topics")
        
        if not plan.get("weak_topics"):
            st.success("🎉 Excellent! You have no weak topics identified (< 60%). Keep practicing intermediate/advanced topics!")
        else:
            for wt in plan["weak_topics"]:
                with st.expander(f"🔴 Weak Area: {wt['topic']} (Current Accuracy: {wt.get('accuracy', 0)}%)", expanded=True):
                    st.markdown(f"**Why Revision is Needed:** {wt['reason']}")
                    st.markdown(f"**Learning Objectives:**")
                    for obj in wt.get("learning_objectives", []):
                        st.markdown(f"- {obj}")
                    st.markdown(f"**Practice Activity:** {wt.get('practice_activity')}")
                    st.markdown(f"**Retest Target:** {wt.get('retest')}")

        # 4-Session Revision Plan
        st.markdown("---")
        st.subheader("📅 4-Session Structured Revision Plan")
        for session in plan.get("personalized_plan", []):
            st.markdown(f"##### 📌 Session {session.get('day')}: {session.get('topic')}")
            for act in session.get("activities", []):
                st.markdown(f"- {act}")

# -----------------------------------------------------------------------------
# 5. EVALUATION & PROMPT ENGINEERING (Techniques comparison & History)
# -----------------------------------------------------------------------------
with tab_eval:
    st.subheader("🧪 Evaluation Test Suite (Format Validity Rate)")
    st.write("Measures real pipeline quality across 12 labelled test cases (valid topics, beginner/intermediate/advanced, empty inputs, off-topic prompts, long inputs).")
    
    if st.button("Run Full Evaluation Suite (12 Cases)", type="primary"):
        with st.spinner("Executing evaluation cases..."):
            def eval_pipeline(topic, mode, diff):
                if mode == "LEARN":
                    prompt = LEARN_PROMPT.format(topic=topic, difficulty=diff)
                    return call_gemini_json(prompt, demo_mode, lambda: demo.explanation(topic, diff))
                elif mode == "QUIZ":
                    prompt = QUIZ_PROMPT.format(topic=topic, difficulty=diff)
                    return call_gemini_json(prompt, demo_mode, lambda: demo.quiz(topic, diff, 5))
                elif mode == "FLASHCARDS":
                    prompt = FLASHCARD_PROMPT.format(topic=topic, difficulty=diff)
                    return call_gemini_json(prompt, demo_mode, lambda: demo.flashcards(topic, diff, 5))
                elif mode == "DIAGNOSTIC":
                    return call_gemini_json(DIAGNOSTIC_PROMPT, demo_mode, lambda: demo.diagnostic())
                return {"status": "error"}

            results_df, metric_val = evaluate(eval_pipeline)
            st.dataframe(results_df, use_container_width=True)
            st.metric("Format Validity Rate", f"{metric_val:.1f}%")
            log_history("EVALUATION", "Ran 12 test cases", f"Metric = {metric_val:.1f}%", "PASSED" if metric_val >= 90 else "FAIL")

    st.markdown("---")
    st.subheader("🔬 Prompt Engineering Technique Comparison")
    st.write("Compare two distinct prompting strategies on any topic:")
    
    comp_topic = st.text_input("Comparison Topic:", "Python List Comprehensions", key="comp_topic")
    if st.button("Compare Techniques"):
        if demo_mode:
            ta = f"**Technique A (Few-Shot Prompting):**\n- Topic: {comp_topic}\n- Definition: Syntactic shorthand to construct lists.\n- Example: `[x**2 for x in range(5)]`\n- Pitfall: Overcomplicating nested comprehensions.\n- Check: How do you filter with `if`?"
            tb = f"**Technique B (Decomposition + Constraints):**\n1. Core prerequisite: Loops and list creation.\n2. Deep explanation: Evaluates expression over iterator with optional filtering.\n3. Example: `evens = [x for x in range(10) if x % 2 == 0]`\n4. Edge case: Memory usage for large iterables (use generator instead).\n5. Self-check: Rewrite a 3-line for-loop into a single comprehension."
        else:
            llm = LLM()
            ta = llm.generate(TECHNIQUE_A_PROMPT.format(topic=comp_topic, difficulty=difficulty))
            tb = llm.generate(TECHNIQUE_B_PROMPT.format(topic=comp_topic, difficulty=difficulty))
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Technique A (Few-Shot Role Prompting)")
            st.markdown(ta)
        with c2:
            st.markdown("### Technique B (Decomposition & Constraint)")
            st.markdown(tb)

    st.markdown("---")
    st.subheader("📜 Timestamped Prompt Version History (`prompt_history.csv`)")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            st.text("".join(lines))
    else:
        st.info("No prompt history logged yet.")
