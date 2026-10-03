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

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & SOPHISTICATED RUST & DARK THEME CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="🦀 PYTHON PULSE | AI Study Assistant",
    page_icon="🦀",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --rust-primary: #CE422B;
    --rust-dark: #9F2D20;
    --rust-light: #F0523A;
    --bg-main: #0B0F14;
    --bg-secondary: #111827;
    --card-bg: #151D29;
    --card-elevated: #1B2533;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-glow: rgba(206, 66, 43, 0.3);
    --text-primary: #F8FAFC;
    --text-muted: #94A3B8;
    --success: #22C55E;
    --warning: #F59E0B;
}

html, body {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}

/* Remove unwanted dark bounding boxes around normal text elements */
p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stMarkdownContainer {
    background-color: transparent !important;
    color: inherit;
}

.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(206, 66, 43, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(55, 118, 171, 0.05) 0%, transparent 40%),
                var(--bg-main);
}

/* Glass & Card Design */
.pulse-card {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.pulse-card:hover {
    border-color: var(--rust-primary);
    box-shadow: 0 12px 32px rgba(206, 66, 43, 0.15);
}

.pulse-hero {
    background: linear-gradient(135deg, rgba(27, 37, 51, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
    border: 1px solid var(--border-glow);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.pulse-hero::after {
    content: '</>';
    position: absolute;
    right: 24px;
    top: 24px;
    font-size: 70px;
    font-weight: 800;
    color: rgba(206, 66, 43, 0.05);
    font-family: 'JetBrains Mono', monospace;
    pointer-events: none;
}

/* 6-Step Visual Journey Tracker */
.journey-tracker {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 12px 20px;
    margin-bottom: 24px;
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
    background-color: var(--card-elevated) !important;
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
    padding: 12px 18px !important;
    margin-bottom: 8px !important;
    transition: all 0.2s ease !important;
}

div[role="radiogroup"] > label:hover {
    border-color: var(--rust-primary) !important;
}

pre, code {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE & NAVIGATION
# -----------------------------------------------------------------------------
HISTORY_FILE = "prompt_history.csv"

if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "🏠 Dashboard"

if "journey_step" not in st.session_state:
    st.session_state["journey_step"] = 1

if "current_topic" not in st.session_state:
    st.session_state["current_topic"] = "Python Functions"

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

# API key check
has_api_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
demo_mode = not has_api_key

def log_history(version: str, change_description: str, problem_or_reason: str, observed_result: str):
    exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "prompt_version", "change_made", "problem_or_reason", "observed_result"])
        writer.writerow([now(), version, change_description, problem_or_reason, observed_result])

def call_gemini_json(prompt: str, fallback_fn):
    if demo_mode:
        return fallback_fn()
    llm = LLM()
    if not llm.available:
        return fallback_fn()
    return llm.generate_json(prompt)

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <div style="font-size: 32px;">🦀</div>
        <div>
            <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.5px; color: #FFF;">PYTHON <span style="color: #CE422B;">PULSE</span></div>
            <div style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">AI Study Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    difficulty = st.selectbox("Global Difficulty", ["Beginner", "Intermediate", "Advanced"], index=0)
    st.markdown("---")

    nav_options = [
        "🏠 Dashboard",
        "📚 Learn",
        "📝 Quiz",
        "🗂 Flashcards",
        "🎯 Diagnostic",
        "🧠 Revision Path",
        "🕘 Prompt History"
    ]

    selected_nav = st.radio("Navigation", nav_options, index=nav_options.index(st.session_state["current_nav"]) if st.session_state["current_nav"] in nav_options else 0, label_visibility="collapsed")
    st.session_state["current_nav"] = selected_nav

# -----------------------------------------------------------------------------
# 4. TOP JOURNEY TRACKER (SYNCED WITH ACTIVE STEP)
# -----------------------------------------------------------------------------
# Map selected_nav to step number
step_map = {
    "🏠 Dashboard": 1,
    "📚 Learn": 2,
    "📝 Quiz": 3,
    "🗂 Flashcards": 4,
    "🎯 Diagnostic": 5,
    "🧠 Revision Path": 6,
    "🕘 Prompt History": 6
}
current_active_step = step_map.get(selected_nav, 1)

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
    if s_num == current_active_step:
        status_cls = "active"
        badge = str(s_num)
    elif s_num < current_active_step:
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
# 5. PAGE ROUTER
# =============================================================================

# -----------------------------------------------------------------------------
# 5.1. 🏠 DASHBOARD
# -----------------------------------------------------------------------------
if selected_nav == "🏠 Dashboard":
    st.markdown("""
    <div class="pulse-hero">
        <div style="font-size: 13px; font-weight: 700; color: #F0523A; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px;">🦀 PYTHON PULSE</div>
        <div style="font-size: 28px; font-weight: 800; color: #FFF; line-height: 1.2; margin-bottom: 10px;">Your AI-Powered Python Learning Companion</div>
        <div style="font-size: 15px; color: #94A3B8; max-width: 600px;">
            Step-by-step concept learning, instant quizzes, flashcards, and diagnostic personalized revision.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="pulse-card" style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 6px;">📚</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFF;">LEARN</div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">Step 2: Master concepts</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Learning →", key="d_btn_l", use_container_width=True):
            st.session_state["current_nav"] = "📚 Learn"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="pulse-card" style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 6px;">📝</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFF;">QUIZ</div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">Step 3: Test knowledge</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Take Quiz →", key="d_btn_q", use_container_width=True):
            st.session_state["current_nav"] = "📝 Quiz"
            st.rerun()

    with c3:
        st.markdown("""
        <div class="pulse-card" style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 6px;">🗂</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFF;">FLASHCARDS</div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">Step 4: Active recall</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Practice →", key="d_btn_f", use_container_width=True):
            st.session_state["current_nav"] = "🗂 Flashcards"
            st.rerun()

    with c4:
        st.markdown("""
        <div class="pulse-card" style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 6px;">🎯</div>
            <div style="font-size: 15px; font-weight: 700; color: #FFF;">DIAGNOSTIC</div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">Step 5: Weak topics</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Assessment →", key="d_btn_d", use_container_width=True):
            st.session_state["current_nav"] = "🎯 Diagnostic"
            st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5.2. 📚 LEARN PAGE (STEP 2)
# -----------------------------------------------------------------------------
elif selected_nav == "📚 Learn":
    st.markdown("""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">📚 Step 2 — Learn Python Concepts</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">Master concepts at your chosen difficulty level with AI-powered structured breakdowns.</div>
    </div>
    """, unsafe_allow_html=True)

    col_in1, col_in2 = st.columns([3, 1])
    with col_in1:
        topic_input = st.text_input(
            "Enter Python Topic:",
            value=st.session_state.get("current_topic", "Python Functions"),
            label_visibility="collapsed"
        )
    with col_in2:
        gen_btn = st.button("✨ Explain Topic", type="primary", use_container_width=True)

    if gen_btn:
        is_valid, err = validate_input(topic_input, "LEARN", difficulty)
        if not is_valid:
            st.error(err.get('message'))
        else:
            clean_topic = topic_input.strip()
            st.session_state["current_topic"] = clean_topic
            with st.spinner(f"AI is preparing your lesson for '{clean_topic}'..."):
                prompt = LEARN_PROMPT.format(topic=clean_topic, difficulty=difficulty)
                res = call_gemini_json(prompt, lambda: demo.explanation(clean_topic, difficulty))
                st.session_state["learn_res"] = res

    if "learn_res" not in st.session_state:
        res = call_gemini_json(LEARN_PROMPT.format(topic=st.session_state["current_topic"], difficulty=difficulty), lambda: demo.explanation(st.session_state["current_topic"], difficulty))
        st.session_state["learn_res"] = res

    res = st.session_state["learn_res"]

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 16px 0 12px 0;">
        <div style="font-size: 20px; font-weight: 800; color: #F0523A;">{res.get('title', st.session_state['current_topic'])}</div>
        <span style="font-size:12px; font-weight:700; background:rgba(206,66,43,0.15); color:#F0523A; padding:4px 10px; border-radius:6px;">{res.get('difficulty', difficulty)}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pulse-card">
        <div style="font-size: 14px; font-weight: 700; color: #F0523A; margin-bottom: 6px;">💡 What is it?</div>
        <div style="font-size: 14px; color: #FFF; line-height: 1.6;">{res.get('definition', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Syntax & Code Example")
    st.code(res.get("example", "# Code Example\npass"), language="python")

    st.markdown(f"""
    <div class="pulse-card">
        <div style="font-size: 14px; font-weight: 700; color: #F0523A; margin-bottom: 6px;">🧠 How it works</div>
        <div style="font-size: 14px; color: #FFF; line-height: 1.6;">{res.get('explanation', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="pulse-card" style="border-left: 4px solid #F59E0B;">
            <div style="font-size: 14px; font-weight: 700; color: #F59E0B; margin-bottom: 6px;">⚠️ Common Mistake</div>
            <div style="font-size: 13px; color: #FFF;">{res.get('common_mistake', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="pulse-card" style="border-left: 4px solid #22C55E;">
            <div style="font-size: 14px; font-weight: 700; color: #4ADE80; margin-bottom: 6px;">🎯 Practice Challenge</div>
            <div style="font-size: 13px; color: #FFF;">{res.get('practice_question', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Quiz (Step 3) →", type="primary", use_container_width=True):
        st.session_state["current_nav"] = "📝 Quiz"
        st.session_state["quiz_curr_idx"] = 0
        st.session_state["quiz_answers"] = {}
        st.session_state.pop("active_quiz", None)
        st.rerun()

# -----------------------------------------------------------------------------
# 5.3. 📝 QUIZ PAGE (STEP 3)
# -----------------------------------------------------------------------------
elif selected_nav == "📝 Quiz":
    topic = st.session_state.get("current_topic", "Python Functions")

    st.markdown(f"""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">📝 Step 3 — Python Quiz</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">Test what you just learned on <b style="color:#F0523A;">{topic}</b> (5 Questions).</div>
    </div>
    """, unsafe_allow_html=True)

    if "active_quiz" not in st.session_state:
        with st.spinner(f"Generating 5 verified questions on {topic}..."):
            prompt = QUIZ_PROMPT.format(topic=topic, difficulty=difficulty, seed=now())
            res = call_gemini_json(prompt, lambda: demo.quiz(topic, difficulty, 5))
            st.session_state["active_quiz"] = res

    quiz_data = st.session_state["active_quiz"]
    questions = quiz_data.get("questions", [])
    total_q = len(questions)
    curr_idx = st.session_state["quiz_curr_idx"]

    if curr_idx < total_q:
        q = questions[curr_idx]
        progress_pct = int(((curr_idx + 1) / total_q) * 100)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
            <span style="font-size:13px; color:#94A3B8;">Topic: <b style="color:#F0523A;">{topic}</b></span>
            <span style="font-size:13px; color:#F0523A; font-weight:700;">Question {curr_idx + 1} of {total_q}</span>
        </div>
        <div style="width:100%; height:6px; background:#262626; border-radius:99px; margin-bottom:20px;">
            <div style="width:{progress_pct}%; height:100%; background:#CE422B; border-radius:99px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pulse-card">
            <div style="font-size: 16px; font-weight: 600; color: #FFF;">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        selected_opt = st.radio("Options:", q["options"], key=f"quiz_opt_{curr_idx}", index=None, label_visibility="collapsed")

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
        correct_count = sum(1 for a in st.session_state["quiz_answers"].values() if a["correct"])
        score_pct = int((correct_count / total_q) * 100) if total_q > 0 else 0

        st.markdown(f"""
        <div class="pulse-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 40px; margin-bottom: 8px;">🎉</div>
            <div style="font-size: 24px; font-weight: 800; color: #FFF; margin-bottom: 4px;">Quiz Complete!</div>
            <div style="font-size: 36px; font-weight: 800; color: #F0523A; margin-bottom: 6px;">{correct_count} / {total_q} ({score_pct}%)</div>
            <div style="font-size: 14px; color: #94A3B8;">{'Great understanding!' if score_pct>=80 else 'Review recommended!'}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Continue to Flashcards (Step 4) →", type="primary", use_container_width=True):
            st.session_state["current_nav"] = "🗂 Flashcards"
            st.session_state["flashcard_idx"] = 0
            st.session_state["flashcard_revealed"] = False
            st.session_state.pop("active_cards", None)
            st.rerun()

# -----------------------------------------------------------------------------
# 5.4. 🗂 FLASHCARDS PAGE (STEP 4)
# -----------------------------------------------------------------------------
elif selected_nav == "🗂 Flashcards":
    topic = st.session_state.get("current_topic", "Python Functions")

    st.markdown(f"""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">🗂 Step 4 — Active-Recall Flashcards</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">Strengthen memory for <b style="color:#F0523A;">{topic}</b>.</div>
    </div>
    """, unsafe_allow_html=True)

    if "active_cards" not in st.session_state:
        with st.spinner(f"Generating flashcards for {topic}..."):
            prompt = FLASHCARD_PROMPT.format(topic=topic, difficulty=difficulty, seed=now())
            res = call_gemini_json(prompt, lambda: demo.flashcards(topic, difficulty, 5))
            st.session_state["active_cards"] = res

    cards = st.session_state["active_cards"].get("flashcards", [])
    fc_idx = st.session_state["flashcard_idx"] % len(cards)
    current_card = cards[fc_idx]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; font-size:13px; color:#94A3B8; margin-bottom:10px;">
        <span>Card {fc_idx + 1} of {len(cards)}</span>
        <span>Active Recall</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state["flashcard_revealed"]:
        st.markdown(f"""
        <div class="pulse-card" style="min-height: 200px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; border: 1px solid #CE422B;">
            <div style="font-size: 12px; font-weight: 700; color: #F0523A; letter-spacing: 1px; margin-bottom: 6px;">QUESTION</div>
            <div style="font-size: 18px; font-weight: 700; color: #FFF; max-width: 600px;">{current_card['front']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reveal Answer", type="primary", use_container_width=True):
            st.session_state["flashcard_revealed"] = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="pulse-card" style="min-height: 200px; text-align:center; border: 1px solid #4ADE80;">
            <div style="font-size: 12px; font-weight: 700; color: #4ADE80; letter-spacing: 1px; margin-bottom: 6px;">ANSWER</div>
            <div style="font-size: 16px; font-weight: 600; color: #FFF; margin-bottom: 10px;">{current_card['back']}</div>
        </div>
        """, unsafe_allow_html=True)
        if current_card.get("example"):
            st.code(current_card["example"], language="python")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            if st.button("← Previous", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] - 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()
        with col_f2:
            if st.button("Got It ✓", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] + 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()
        with col_f3:
            if st.button("Next →", use_container_width=True):
                st.session_state["flashcard_idx"] = (st.session_state["flashcard_idx"] + 1) % len(cards)
                st.session_state["flashcard_revealed"] = False
                st.rerun()

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Diagnostic Assessment (Step 5) →", type="primary", use_container_width=True):
        st.session_state["current_nav"] = "🎯 Diagnostic"
        st.session_state["diag_curr_idx"] = 0
        st.session_state["diag_answers"] = {}
        st.session_state.pop("diag_content", None)
        st.rerun()

# -----------------------------------------------------------------------------
# 5.5. 🎯 DIAGNOSTIC PAGE (STEP 5)
# -----------------------------------------------------------------------------
elif selected_nav == "🎯 Diagnostic":
    st.markdown("""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">🎯 Step 5 — Diagnostic Assessment</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">10 Questions across core Python topics to detect weak areas.</div>
    </div>
    """, unsafe_allow_html=True)

    if "diag_content" not in st.session_state:
        with st.spinner("Generating 10 diagnostic assessment questions..."):
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
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
            <span style="font-size:13px; color:#94A3B8;">Topic: <b style="color:#F0523A;">{dq.get('topic', 'Python')}</b></span>
            <span style="font-size:13px; color:#F0523A; font-weight:700;">{curr_d_idx + 1} / {total_dq}</span>
        </div>
        <div style="width:100%; height:6px; background:#262626; border-radius:99px; margin-bottom:18px;">
            <div style="width:{progress_pct}%; height:100%; background:#CE422B; border-radius:99px;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pulse-card">
            <div style="font-size: 15px; font-weight: 600; color: #FFF;">{dq['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        d_opt = st.radio("Options:", dq["options"], key=f"d_ans_{curr_d_idx}", index=None, label_visibility="collapsed")

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
        eval_list = list(st.session_state["diag_answers"].values())
        perf = calculate_performance(eval_list)
        st.session_state["diag_perf"] = perf

        st.markdown(f"""
        <div class="pulse-card" style="text-align:center; padding:28px 20px;">
            <div style="font-size: 36px; margin-bottom: 6px;">📊</div>
            <div style="font-size: 22px; font-weight: 800; color: #FFF; margin-bottom: 4px;">Diagnostic Skill Profile</div>
            <div style="font-size: 32px; font-weight: 800; color: #F0523A; margin-bottom: 4px;">{perf['overall_score']}%</div>
            <div style="font-size: 13px; color: #94A3B8;">({perf['total_correct']}/{perf['total_questions']} Questions Correct)</div>
        </div>
        """, unsafe_allow_html=True)

        for t_stat in perf["topics"]:
            acc = t_stat["accuracy"]
            bar_color = "#4ADE80" if acc >= 80 else ("#F59E0B" if acc >= 60 else "#CE422B")
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; margin-bottom:2px;">
                    <span>{t_stat['topic']}</span>
                    <span style="color:{bar_color};">{acc}% ({t_stat['status']})</span>
                </div>
                <div style="width:100%; height:7px; background:#262626; border-radius:99px;">
                    <div style="width:{acc}%; height:100%; background:{bar_color}; border-radius:99px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Generate Personalized Revision Path (Step 6) →", type="primary", use_container_width=True):
            st.session_state["current_nav"] = "🧠 Revision Path"
            st.session_state.pop("revision_plan", None)
            st.rerun()

# -----------------------------------------------------------------------------
# 5.6. 🧠 REVISION PATH PAGE (STEP 6)
# -----------------------------------------------------------------------------
elif selected_nav == "🧠 Revision Path":
    st.markdown("""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">🧠 Step 6 — Personalized Revision Path</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">4-Session targeted roadmap focusing on weak areas.</div>
    </div>
    """, unsafe_allow_html=True)

    perf = st.session_state.get("diag_perf", calculate_performance([{"topic": "Functions", "correct": False}, {"topic": "Loops", "correct": False}, {"topic": "Lists", "correct": True}]))

    if "revision_plan" not in st.session_state:
        with st.spinner("Synthesizing personalized 4-session revision plan..."):
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

    st.markdown("### 🔴 Priority Weak Topics")
    for p_idx, wt in enumerate(plan.get("weak_topics", []), 1):
        st.markdown(f"""
        <div class="pulse-card" style="border-left: 4px solid #CE422B; margin-bottom: 12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <div style="font-size: 16px; font-weight: 700; color: #FFF;">Priority {p_idx} • {wt['topic']}</div>
                <span style="font-size:12px; font-weight:700; color:#F0523A;">Accuracy: {wt.get('accuracy', 0)}%</span>
            </div>
            <div style="font-size: 13px; color: #94A3B8; margin-bottom: 8px;">{wt.get('reason', '')}</div>
            <ul style="font-size: 13px; color: #FFF; margin: 0 0 8px 18px;">
                {''.join(f'<li>{obj}</li>' for obj in wt.get('learning_objectives', []))}
            </ul>
            <div style="font-size: 12px; color: #4ADE80;">Challenge: {wt.get('practice_activity')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📅 4-Session Structured Learning Path")
    for s in plan.get("personalized_plan", []):
        st.markdown(f"""
        <div class="pulse-card" style="border-left: 4px solid #F0523A; margin-bottom: 10px;">
            <div style="font-size: 15px; font-weight: 700; color: #F0523A; margin-bottom: 4px;">📌 Session {s.get('day')}: {s.get('topic')}</div>
            <ul style="font-size: 13px; color: #FFF; margin: 0 0 0 18px;">
                {''.join(f'<li style="margin-bottom: 3px;">{act}</li>' for act in s.get('activities', []))}
            </ul>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5.7. 🕘 PROMPT HISTORY PAGE
# -----------------------------------------------------------------------------
elif selected_nav == "🕘 Prompt History":
    st.markdown("""
    <div>
        <div style="font-size: 26px; font-weight: 800; color: #FFF;">🕘 Timestamped Prompt Version History</div>
        <div style="font-size: 14px; color: #94A3B8; margin-bottom: 18px;">Chronological prompt development log.</div>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No prompt history logged yet.")
