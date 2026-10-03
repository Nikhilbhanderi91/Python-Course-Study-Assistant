import os
import json
import csv
import streamlit as st
import pandas as pd
from datetime import datetime

from llm import LLM
from prompts import (
    LEARN_PROMPT,
    QUIZ_PROMPT,
    FLASHCARD_PROMPT,
    DIAGNOSTIC_PROMPT,
    LEARNING_PATH_PROMPT
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

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & SOPHISTICATED RUST-INSPIRED THEME CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="🦀 PYTHON PULSE | Step-by-Step AI Learning",
    page_icon="🦀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --rust-primary: #CE422B;
    --rust-dark: #9F2D20;
    --rust-light: #F0523A;
    --bg-main: #0F0F0F;
    --bg-secondary: #171717;
    --card-bg: #1F1F1F;
    --border-subtle: #333333;
    --text-primary: #FFFFFF;
    --text-muted: #A3A3A3;
    --success: #4ADE80;
    --warning: #F59E0B;
}

/* Global Reset */
html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    background-color: var(--bg-main);
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-main);
    max-width: 900px;
    margin: 0 auto;
}

/* Top Navigation Bar */
.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0 20px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 24px;
}

.brand-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--text-primary);
}

.brand-logo span {
    color: var(--rust-primary);
}

/* Step Progress Tracker */
.journey-tracker {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 14px 20px;
    margin-bottom: 32px;
    overflow-x: auto;
}

.journey-step {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    white-space: nowrap;
}

.journey-step.active {
    color: var(--rust-light);
    font-weight: 700;
}

.journey-step.completed {
    color: var(--rust-primary);
}

.journey-divider {
    color: var(--border-subtle);
    font-size: 14px;
    margin: 0 4px;
}

.step-indicator-circle {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
    background: #262626;
    color: var(--text-muted);
    border: 1px solid var(--border-subtle);
}

.journey-step.active .step-indicator-circle {
    background: var(--rust-primary);
    color: #FFF;
    border-color: var(--rust-light);
    box-shadow: 0 0 12px rgba(206, 66, 43, 0.4);
}

.journey-step.completed .step-indicator-circle {
    background: var(--rust-dark);
    color: #FFF;
    border-color: var(--rust-primary);
}

/* Card Styling */
.rust-card {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
    transition: all 0.2s ease;
}

.rust-card:hover {
    border-color: #444444;
}

.topic-select-card {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.2s ease;
    cursor: pointer;
    margin-bottom: 12px;
}

.topic-select-card:hover {
    border-color: var(--rust-primary);
    transform: translateY(-2px);
}

.topic-select-card.selected {
    border-color: var(--rust-primary);
    background: rgba(206, 66, 43, 0.08);
}

/* Buttons */
.stButton>button {
    background: var(--rust-primary) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: 1px solid var(--rust-light) !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    background: var(--rust-light) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(206, 66, 43, 0.35) !important;
}

.stTextInput>div>div>input {
    background-color: var(--bg-secondary) !important;
    color: #FFF !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
}

.stTextInput>div>div>input:focus {
    border-color: var(--rust-primary) !important;
    box-shadow: 0 0 0 1px var(--rust-primary) !important;
}

/* Clean Radio option blocks */
div[role="radiogroup"] > label {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    transition: all 0.2s ease !important;
}

div[role="radiogroup"] > label:hover {
    border-color: var(--rust-primary) !important;
}

/* Code */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE & JOURNEY STEP MANAGEMENT
# -----------------------------------------------------------------------------
# Steps: 1: TOPIC, 2: LEARN, 3: QUIZ, 4: FLASHCARDS, 5: DIAGNOSTIC, 6: REVISION
if "journey_step" not in st.session_state:
    st.session_state["journey_step"] = 1

if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = "Python Functions"

if "selected_difficulty" not in st.session_state:
    st.session_state["selected_difficulty"] = "Beginner"

if "quiz_curr_idx" not in st.session_state:
    st.session_state["quiz_curr_idx"] = 0

if "quiz_answers" not in st.session_state:
    st.session_state["quiz_answers"] = {}

if "diag_curr_idx" not in st.session_state:
    st.session_state["diag_curr_idx"] = 0

if "diag_answers" not in st.session_state:
    st.session_state["diag_answers"] = {}

if "flashcard_idx" not in st.session_state:
    st.session_state["flashcard_idx"] = 0

if "flashcard_revealed" not in st.session_state:
    st.session_state["flashcard_revealed"] = False

# Helper to call LLM or Demo fallback
has_api_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
demo_mode = not has_api_key

def call_gemini_json(prompt: str, fallback_fn):
    if demo_mode:
        return fallback_fn()
    llm = LLM()
    if not llm.available:
        return fallback_fn()
    return llm.generate_json(prompt)

# -----------------------------------------------------------------------------
# 3. TOP NAVIGATION & JOURNEY STEP PROGRESS BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="top-nav">
    <div class="brand-logo">🦀 PYTHON <span>PULSE</span></div>
    <div style="font-size: 13px; color: #A3A3A3; font-weight: 600;">AI Python Learning Assistant</div>
</div>
""", unsafe_allow_html=True)

# 6-Step Visual Journey Tracker
steps = [
    (1, "Topic"),
    (2, "Learn"),
    (3, "Quiz"),
    (4, "Flashcards"),
    (5, "Diagnostic"),
    (6, "Revision")
]

tracker_html = '<div class="journey-tracker">'
for idx, (s_num, s_name) in enumerate(steps):
    c_step = st.session_state["journey_step"]
    if s_num == c_step:
        status_cls = "active"
        badge = str(s_num)
    elif s_num < c_step:
        status_cls = "completed"
        badge = "✓"
    else:
        status_cls = "future"
        badge = str(s_num)
    
    tracker_html += f"""
    <div class="journey-step {status_cls}">
        <div class="step-indicator-circle">{badge}</div>
        <span>{s_name}</span>
    </div>
    """
    if idx < len(steps) - 1:
        tracker_html += '<div class="journey-divider">──</div>'

tracker_html += '</div>'
st.markdown(tracker_html, unsafe_allow_html=True)

# =============================================================================
# 4. STEP-BY-STEP GUIDED VIEWS
# =============================================================================

# -----------------------------------------------------------------------------
# STEP 1 — CHOOSE TOPIC
# -----------------------------------------------------------------------------
if st.session_state["journey_step"] == 1:
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="font-size: 28px; font-weight: 800; color: #FFF; margin-bottom: 6px;">What do you want to learn?</div>
        <div style="font-size: 15px; color: #A3A3A3;">Choose a Python topic to begin your guided learning journey.</div>
    </div>
    """, unsafe_allow_html=True)

    # Topic catalog
    beginner_topics = ["Python Syntax", "Variables & Data Types", "Strings", "Lists", "Tuples & Sets", "Dictionaries", "Conditions (if/else)", "Loops (for/while)", "Python Functions"]
    intermediate_topics = ["List Comprehensions", "Lambda Functions", "Recursion", "Modules & Packages", "File Handling", "Exception Handling", "OOP & Classes", "Inheritance"]
    advanced_topics = ["Decorators", "Generators & Iterators", "Context Managers", "Asyncio & Concurrency", "Memory Management", "Testing & Debugging"]

    category = st.radio("Level Filter", ["Beginner", "Intermediate", "Advanced"], horizontal=True, label_visibility="collapsed")
    
    if category == "Beginner":
        active_list = beginner_topics
    elif category == "Intermediate":
        active_list = intermediate_topics
    else:
        active_list = advanced_topics

    # Select box or grid
    selected = st.selectbox("Select Topic:", active_list, index=active_list.index(st.session_state.get("selected_topic", active_list[0])) if st.session_state.get("selected_topic") in active_list else 0)
    st.session_state["selected_topic"] = selected

    # Custom topic input option
    custom_topic = st.text_input("Or type a custom Python topic:", placeholder="e.g. Dictionary Comprehensions, Args & Kwargs")
    if custom_topic.strip():
        st.session_state["selected_topic"] = custom_topic.strip()

    difficulty = st.selectbox("Select Difficulty Level:", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(category))
    st.session_state["selected_difficulty"] = difficulty

    st.markdown(f"""
    <div class="rust-card" style="border-left: 4px solid #CE422B; margin-top: 20px;">
        <div style="font-size: 13px; font-weight: 700; color: #F0523A; margin-bottom: 4px;">READY TO START</div>
        <div style="font-size: 18px; font-weight: 700; color: #FFF;">🐍 {st.session_state['selected_topic']}</div>
        <div style="font-size: 13px; color: #A3A3A3;">Difficulty: {st.session_state['selected_difficulty']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Learning Journey →", type="primary", use_container_width=True):
        st.session_state["journey_step"] = 2
        st.session_state.pop("learn_content", None)
        st.session_state.pop("quiz_content", None)
        st.session_state.pop("flashcard_content", None)
        st.rerun()

# -----------------------------------------------------------------------------
# STEP 2 — LEARN
# -----------------------------------------------------------------------------
elif st.session_state["journey_step"] == 2:
    topic = st.session_state["selected_topic"]
    diff = st.session_state["selected_difficulty"]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 20px;">
        <div>
            <div style="font-size: 26px; font-weight: 800; color: #FFF;">Learn {topic}</div>
            <div style="font-size: 14px; color: #A3A3A3;">{diff} Level • Step 2 of 6</div>
        </div>
        <span style="font-size:12px; color:#F0523A; font-weight:700;">STEP 2 / 6</span>
    </div>
    """, unsafe_allow_html=True)

    if "learn_content" not in st.session_state:
        with st.spinner(f"✨ AI is preparing your lesson on {topic}..."):
            prompt = LEARN_PROMPT.format(topic=topic, difficulty=diff)
            res = call_gemini_json(prompt, lambda: demo.explanation(topic, diff))
            st.session_state["learn_content"] = res

    content = st.session_state["learn_content"]

    st.markdown(f"""
    <div class="rust-card">
        <div style="font-size: 14px; font-weight: 700; color: #F0523A; margin-bottom: 8px;">💡 What is it? (Definition)</div>
        <div style="font-size: 15px; color: #FFF; line-height: 1.6;">{content.get('definition', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Syntax & Example")
    st.code(content.get("example", "# Code Example\npass"), language="python")

    st.markdown(f"""
    <div class="rust-card">
        <div style="font-size: 14px; font-weight: 700; color: #F0523A; margin-bottom: 8px;">🧠 How it works</div>
        <div style="font-size: 14px; color: #FFF; line-height: 1.6;">{content.get('explanation', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rust-card" style="border-left: 4px solid #F59E0B;">
        <div style="font-size: 14px; font-weight: 700; color: #F59E0B; margin-bottom: 8px;">⚠️ Common Mistake</div>
        <div style="font-size: 14px; color: #FFF; line-height: 1.6;">{content.get('common_mistake', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        if st.button("← Back to Topics"):
            st.session_state["journey_step"] = 1
            st.rerun()
    with col_b2:
        if st.button("Continue to Quiz (Step 3) →", type="primary", use_container_width=True):
            st.session_state["journey_step"] = 3
            st.session_state["quiz_curr_idx"] = 0
            st.session_state["quiz_answers"] = {}
            st.session_state.pop("quiz_content", None)
            st.rerun()

# -----------------------------------------------------------------------------
# STEP 3 — QUIZ
# -----------------------------------------------------------------------------
elif st.session_state["journey_step"] == 3:
    topic = st.session_state["selected_topic"]
    diff = st.session_state["selected_difficulty"]

    if "quiz_content" not in st.session_state:
        with st.spinner(f"✨ Generating 5 verified quiz questions for {topic}..."):
            prompt = QUIZ_PROMPT.format(topic=topic, difficulty=diff, seed=now())
            res = call_gemini_json(prompt, lambda: demo.quiz(topic, diff, 5))
            st.session_state["quiz_content"] = res

    quiz_data = st.session_state["quiz_content"]
    questions = quiz_data.get("questions", [])
    total_q = len(questions)
    curr_idx = st.session_state["quiz_curr_idx"]

    if curr_idx < total_q:
        q = questions[curr_idx]
        progress_pct = int(((curr_idx + 1) / total_q) * 100)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 12px;">
            <div>
                <div style="font-size: 26px; font-weight: 800; color: #FFF;">Test Your Understanding</div>
                <div style="font-size: 14px; color: #A3A3A3;">Topic: <b style="color:#F0523A;">{topic}</b></div>
            </div>
            <span style="font-size:13px; color:#F0523A; font-weight:700;">Question {curr_idx + 1} of {total_q}</span>
        </div>
        <div style="width:100%; height:6px; background:#262626; border-radius:99px; margin-bottom:24px;">
            <div style="width:{progress_pct}%; height:100%; background:#CE422B; border-radius:99px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rust-card">
            <div style="font-size: 12px; font-weight: 700; color: #F0523A; margin-bottom: 6px;">QUESTION 0{curr_idx + 1}</div>
            <div style="font-size: 16px; font-weight: 600; color: #FFF;">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        selected_opt = st.radio("Options:", q["options"], key=f"q_ans_{curr_idx}", index=None, label_visibility="collapsed")

        # Answer check
        if st.button("Submit Answer →", type="primary", use_container_width=True):
            if not selected_opt:
                st.warning("Please choose an answer.")
            else:
                is_correct = (selected_opt == q["correct_answer"])
                st.session_state["quiz_answers"][curr_idx] = {
                    "chosen": selected_opt,
                    "correct": is_correct,
                    "correct_answer": q["correct_answer"],
                    "explanation": q["explanation"]
                }
                st.session_state["quiz_curr_idx"] += 1
                st.rerun()

    else:
        # Quiz Summary
        correct_count = sum(1 for a in st.session_state["quiz_answers"].values() if a["correct"])
        score_pct = int((correct_count / total_q) * 100) if total_q > 0 else 0

        st.markdown(f"""
        <div class="rust-card" style="text-align: center; padding: 36px 20px;">
            <div style="font-size: 44px; margin-bottom: 12px;">🎉</div>
            <div style="font-size: 26px; font-weight: 800; color: #FFF; margin-bottom: 8px;">Quiz Complete!</div>
            <div style="font-size: 40px; font-weight: 800; color: #F0523A; margin-bottom: 8px;">{correct_count} / {total_q}</div>
            <div style="font-size: 16px; color: #A3A3A3; margin-bottom: 24px;">Accuracy: {score_pct}% • { 'Good understanding!' if score_pct>=80 else 'Review recommended!' }</div>
        </div>
        """, unsafe_allow_html=True)

        # Review questions
        for idx, (i, ans_data) in enumerate(st.session_state["quiz_answers"].items()):
            icon = "✓ Correct" if ans_data["correct"] else "✗ Incorrect"
            color = "#4ADE80" if ans_data["correct"] else "#EF4444"
            st.markdown(f"""
            <div class="rust-card" style="border-left: 3px solid {color}; margin-bottom: 10px;">
                <div style="font-size: 13px; font-weight: 700; color: {color};">{icon} - Q{i+1}</div>
                <div style="font-size: 13px; color: #A3A3A3; margin-top: 4px;"><i>Explanation:</i> {ans_data['explanation']}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Continue to Flashcards (Step 4) →", type="primary", use_container_width=True):
            st.session_state["journey_step"] = 4
            st.session_state["flashcard_idx"] = 0
            st.session_state["flashcard_revealed"] = False
            st.session_state.pop("flashcard_content", None)
            st.rerun()

# -----------------------------------------------------------------------------
# STEP 4 — FLASHCARDS
# -----------------------------------------------------------------------------
elif st.session_state["journey_step"] == 4:
    topic = st.session_state["selected_topic"]
    diff = st.session_state["selected_difficulty"]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 20px;">
        <div>
            <div style="font-size: 26px; font-weight: 800; color: #FFF;">Strengthen Your Memory</div>
            <div style="font-size: 14px; color: #A3A3A3;">Active Recall • Topic: <b style="color:#F0523A;">{topic}</b></div>
        </div>
        <span style="font-size:12px; color:#F0523A; font-weight:700;">STEP 4 / 6</span>
    </div>
    """, unsafe_allow_html=True)

    if "flashcard_content" not in st.session_state:
        with st.spinner(f"✨ Creating 5 flashcards for {topic}..."):
            prompt = FLASHCARD_PROMPT.format(topic=topic, difficulty=diff, seed=now())
            res = call_gemini_json(prompt, lambda: demo.flashcards(topic, diff, 5))
            st.session_state["flashcard_content"] = res

    cards = st.session_state["flashcard_content"].get("flashcards", [])
    fc_idx = st.session_state["flashcard_idx"] % len(cards)
    current_card = cards[fc_idx]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:13px; color:#A3A3A3; margin-bottom:12px;">
        <span>Card {fc_idx + 1} of {len(cards)}</span>
        <span>Active Recall Practice</span>
    </div>
    """, unsafe_allow_html=True)

    # Large single flashcard
    if not st.session_state["flashcard_revealed"]:
        st.markdown(f"""
        <div class="rust-card" style="min-height: 220px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; border: 1px solid #CE422B;">
            <div style="font-size: 12px; font-weight: 700; color: #F0523A; letter-spacing: 1px; margin-bottom: 8px;">QUESTION</div>
            <div style="font-size: 18px; font-weight: 700; color: #FFF; max-width: 600px;">{current_card['front']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reveal Answer", type="primary", use_container_width=True):
            st.session_state["flashcard_revealed"] = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="rust-card" style="min-height: 220px; text-align:center; border: 1px solid #4ADE80;">
            <div style="font-size: 12px; font-weight: 700; color: #4ADE80; letter-spacing: 1px; margin-bottom: 8px;">ANSWER</div>
            <div style="font-size: 16px; font-weight: 600; color: #FFF; margin-bottom: 12px;">{current_card['back']}</div>
        </div>
        """, unsafe_allow_html=True)
        if current_card.get("example"):
            st.code(current_card["example"], language="python")

        col_fc1, col_fc2, col_fc3 = st.columns(3)
        with col_fc1:
            if st.button("← Previous Card", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] - 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()
        with col_fc2:
            if st.button("Got It ✓", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] + 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()
        with col_fc3:
            if st.button("Next Card →", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] + 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()

    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Diagnostic Assessment (Step 5) →", type="primary", use_container_width=True):
        st.session_state["journey_step"] = 5
        st.session_state["diag_curr_idx"] = 0
        st.session_state["diag_answers"] = {}
        st.session_state.pop("diag_content", None)
        st.rerun()

# -----------------------------------------------------------------------------
# STEP 5 — DIAGNOSTIC ASSESSMENT
# -----------------------------------------------------------------------------
elif st.session_state["journey_step"] == 5:
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 20px;">
        <div>
            <div style="font-size: 26px; font-weight: 800; color: #FFF;">Discover Your Weak Topics</div>
            <div style="font-size: 14px; color: #A3A3A3;">10 Questions across core Python topics for diagnostic analysis.</div>
        </div>
        <span style="font-size:12px; color:#F0523A; font-weight:700;">STEP 5 / 6</span>
    </div>
    """, unsafe_allow_html=True)

    if "diag_content" not in st.session_state:
        with st.spinner("✨ Generating 10 diagnostic questions covering Python fundamentals..."):
            res = call_gemini_json(DIAGNOSTIC_PROMPT, lambda: demo.diagnostic())
            st.session_state["diag_content"] = res

    diag_data = st.session_state["diag_content"]
    d_questions = diag_data.get("questions", [])
    total_dq = len(d_questions)
    curr_d_idx = st.session_state["diag_curr_idx"]

    if curr_d_idx < total_dq:
        dq = d_questions[curr_d_idx]
        progress_pct = int(((curr_d_idx + 1) / total_dq) * 100)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
            <span style="font-size:13px; color:#A3A3A3;">Topic: <b style="color:#F0523A;">{dq.get('topic', 'Python')}</b></span>
            <span style="font-size:13px; color:#F0523A; font-weight:700;">{curr_d_idx + 1} / {total_dq}</span>
        </div>
        <div style="width:100%; height:6px; background:#262626; border-radius:99px; margin-bottom:20px;">
            <div style="width:{progress_pct}%; height:100%; background:#CE422B; border-radius:99px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rust-card">
            <div style="font-size: 16px; font-weight: 600; color: #FFF;">{dq['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        d_opt = st.radio("Choose answer:", dq["options"], key=f"d_ans_{curr_d_idx}", index=None, label_visibility="collapsed")

        if st.button("Submit & Next →", type="primary", use_container_width=True):
            if not d_opt:
                st.warning("Please choose an answer.")
            else:
                is_corr = (d_opt == dq["correct_answer"])
                st.session_state["diag_answers"][curr_d_idx] = {
                    "topic": dq.get("topic", "Python"),
                    "question": dq["question"],
                    "chosen": d_opt,
                    "correct_answer": dq["correct_answer"],
                    "correct": is_corr
                }
                st.session_state["diag_curr_idx"] += 1
                st.rerun()

    else:
        # Diagnostic Assessment Complete
        eval_list = list(st.session_state["diag_answers"].values())
        perf = calculate_performance(eval_list)
        st.session_state["diag_perf"] = perf

        st.markdown(f"""
        <div class="rust-card" style="text-align:center; padding:30px 20px;">
            <div style="font-size: 40px; margin-bottom: 8px;">📊</div>
            <div style="font-size: 24px; font-weight: 800; color: #FFF; margin-bottom: 6px;">Your Python Skill Profile</div>
            <div style="font-size: 36px; font-weight: 800; color: #F0523A; margin-bottom: 6px;">{perf['overall_score']}%</div>
            <div style="font-size: 14px; color: #A3A3A3;">Diagnostic Score ({perf['total_correct']}/{perf['total_questions']} Questions Correct)</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Skill Breakdown by Topic")
        for t_stat in perf["topics"]:
            acc = t_stat["accuracy"]
            bar_color = "#4ADE80" if acc >= 80 else ("#F59E0B" if acc >= 60 else "#CE422B")
            st.markdown(f"""
            <div style="margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:4px;">
                    <span>{t_stat['topic']}</span>
                    <span style="color:{bar_color};">{acc}% ({t_stat['status']})</span>
                </div>
                <div style="width:100%; height:8px; background:#262626; border-radius:99px;">
                    <div style="width:{acc}%; height:100%; background:{bar_color}; border-radius:99px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("Generate My Personalized Revision Path (Step 6) →", type="primary", use_container_width=True):
            st.session_state["journey_step"] = 6
            st.session_state.pop("revision_plan", None)
            st.rerun()

# -----------------------------------------------------------------------------
# STEP 6 — PERSONALIZED REVISION
# -----------------------------------------------------------------------------
elif st.session_state["journey_step"] == 6:
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom: 20px;">
        <div>
            <div style="font-size: 26px; font-weight: 800; color: #FFF;">Your Personalized Revision Path</div>
            <div style="font-size: 14px; color: #A3A3A3;">Targeted 4-session plan generated from your diagnostic results.</div>
        </div>
        <span style="font-size:12px; color:#4ADE80; font-weight:700;">JOURNEY COMPLETE ✓</span>
    </div>
    """, unsafe_allow_html=True)

    perf = st.session_state.get("diag_perf", calculate_performance([{"topic": "Functions", "correct": False}, {"topic": "Loops", "correct": False}, {"topic": "Lists", "correct": True}]))

    if "revision_plan" not in st.session_state:
        with st.spinner("✨ AI is synthesizing your 4-session revision roadmap..."):
            perf_summary_str = f"Overall Accuracy: {perf['overall_score']}%, Total Correct: {perf['total_correct']}/{perf['total_questions']}"
            prompt_lp = LEARNING_PATH_PROMPT.format(
                performance_summary=perf_summary_str,
                weak_topics=", ".join(perf["weak_topics"]) if perf["weak_topics"] else "None",
                developing_topics=", ".join(perf["developing_topics"]) if perf["developing_topics"] else "None",
                strong_topics=", ".join(perf["strong_topics"]) if perf["strong_topics"] else "None"
            )
            res = call_gemini_json(prompt_lp, lambda: demo.learning_path(perf))
            st.session_state["revision_plan"] = res

    plan = st.session_state["revision_plan"]

    # Priority weak topics
    st.markdown("### 🔴 Priority Weak Topics")
    if not plan.get("weak_topics"):
        st.success("🎉 Excellent! No weak topics (<60%) were detected. You are ready for advanced Python concepts.")
    else:
        for p_idx, wt in enumerate(plan.get("weak_topics", []), 1):
            st.markdown(f"""
            <div class="rust-card" style="border-left: 4px solid #CE422B; margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div style="font-size: 16px; font-weight: 700; color: #FFF;">Priority {p_idx} • {wt['topic']}</div>
                    <span style="font-size:12px; font-weight:700; color:#F0523A;">Current: {wt.get('accuracy', 0)}% → Target: 80%</span>
                </div>
                <div style="font-size: 13px; color: #A3A3A3; margin-bottom: 10px;">{wt.get('reason', '')}</div>
                <div style="font-size: 13px; color: #FFF; font-weight:600; margin-bottom: 4px;">Focus on:</div>
                <ul style="font-size: 13px; color: #A3A3A3; margin: 0 0 10px 18px;">
                    {''.join(f'<li>{obj}</li>' for obj in wt.get('learning_objectives', []))}
                </ul>
                <div style="font-size: 12px; color: #4ADE80;">Practice Challenge: {wt.get('practice_activity')}</div>
            </div>
            """, unsafe_allow_html=True)

    # 4-Session Timeline
    st.markdown("### 📅 4-Session Structured Learning Path")
    for s in plan.get("personalized_plan", []):
        st.markdown(f"""
        <div class="rust-card" style="border-left: 4px solid #F0523A; margin-bottom: 12px;">
            <div style="font-size: 15px; font-weight: 700; color: #F0523A; margin-bottom: 6px;">📌 Session {s.get('day')}: {s.get('topic')}</div>
            <ul style="font-size: 13px; color: #FFF; margin: 0 0 0 18px;">
                {''.join(f'<li style="margin-bottom: 4px;">{act}</li>' for act in s.get('activities', []))}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Start a New Learning Journey (Step 1) ↺", type="primary", use_container_width=True):
        st.session_state["journey_step"] = 1
        st.session_state["quiz_curr_idx"] = 0
        st.session_state["diag_curr_idx"] = 0
        st.session_state["quiz_answers"] = {}
        st.session_state["diag_answers"] = {}
        st.rerun()
