# 🦀 PYTHON PULSE — Team Roles & Prompt Engineering Task Distribution

**Project**: Python Course Study Assistant (`PYTHON PULSE`)  
**Hackathon Target**: 3-Hour AI Education Prototype  
**Architecture**: Google Gemini API (`google-genai` SDK) + Streamlit + Guardrails + Prompt Chaining  

---

## 👥 Team Roster & Module Ownership

| Member | Name | Role / Core Ownership | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Nikhil** | **Team Lead & Core LLM / UI Integration** | • Gemini Client integration (`llm.py`)<br>• Streamlit app orchestration & Step-by-Step Flow (`app.py`)<br>• Git Repository management & final presentation flow |
| **Member 2** | **Devendrasinh** | **Prompt Engineering & Schema Design** | • Design and optimize system & role prompts (`prompts.py`)<br>• Few-shot exemplars and difficulty level adaptation (Beginner / Intermediate / Advanced)<br>• Techniques comparison (Technique A vs Technique B) |
| **Member 3** | **Phani** | **Guardrails, Validation & Performance Analytics** | • Input & Output validation guardrails (`utils.py`)<br>• Off-topic query detection and JSON schema enforcement<br>• Accuracy calculation & weak topic identification algorithms |
| **Member 4** | **Niki** | **Diagnostic Pipeline & Evaluation Suite** | • Diagnostic assessment & 4-session revision plan generation (`prompts.py`, `evaluator.py`)<br>• 12-case evaluation benchmark with **Format Validity Rate** metric<br>• Timestamped prompt iteration history (`prompt_history.csv`) |

---

## 📋 Detailed Member Task Breakdown & Action Items

### 1. 👤 Member 1 — Nikhil (Lead & UI/Architecture)
* **Goal**: Ensure seamless execution, error-free API calls, and a guided user journey.
* **Key Tasks**:
  1. **Gemini SDK Setup (`llm.py`)**:
     - Maintain `genai.Client(api_key=...)` using `gemini-2.5-flash`.
     - Ensure safe fallback to demo mock mode if no API key is set.
  2. **UI & State Orchestration (`app.py`)**:
     - Connect the 6-step guided learning path:
       $$\text{① Topic} \longrightarrow \text{② Learn} \longrightarrow \text{③ Quiz} \longrightarrow \text{④ Flashcards} \longrightarrow \text{⑤ Diagnostic} \longrightarrow \text{⑥ Revision}$$
     - Keep the UI responsive, dark-themed, and free of clutter.
  3. **Live Demonstration Lead**:
     - Walk judges through a full demo: `Lists (Beginner)` $\rightarrow$ `Quiz` $\rightarrow$ `Flashcards` $\rightarrow$ `Diagnostic` $\rightarrow$ `AI Revision Path`.

---

### 2. 👤 Member 2 — Devendrasinh (Prompt Engineering & Adaptability)
* **Goal**: Maximize teaching quality, difficulty adaptation, and structured output adherence.
* **Key Tasks**:
  1. **Role & Few-Shot Prompting (`prompts.py`)**:
     - **Role Prompting**: Explicit expert Python tutor persona with strict educational constraints.
     - **Few-Shot Prompting**: Provide concrete reference structures (e.g. list indexing and append examples).
  2. **Difficulty Adaptation**:
     - **Beginner**: Clear definitions, syntax templates, line-by-line explanations, common rookie mistakes.
     - **Intermediate**: Practical applications, best practices, error handling.
     - **Advanced**: Internal runtime mechanics, decorators/generators, performance & design trade-offs.
  3. **Prompt Technique Comparison**:
     - Prepare **Technique A** (Few-Shot Role Prompting) vs **Technique B** (Decomposition + Constraint Prompting) for live judge comparison.

---

### 3. 👤 Member 3 — Phani (Guardrails, Security & Analytics)
* **Goal**: Guarantee zero hallucinations, complete schema reliability, and objective performance scoring.
* **Key Tasks**:
  1. **Dual-Layer Guardrails (`utils.py`)**:
     - **Input Validation**: Filter empty topics, excessively long inputs (>300 chars), and off-topic queries (e.g., weather, politics, sports).
     - **Output Validation**: Strip markdown fences, validate JSON keys, ensure exactly 5 MCQs (4 options each) and 5 flashcards.
  2. **Objective Quiz & Diagnostic Scoring**:
     - Compute genuine metrics without fabricating data:
       - **Strong**: $\ge 80\%$
       - **Developing**: $60\% - 79\%$
       - **Weak**: $< 60\%$
  3. **Error Handling**:
     - Return user-friendly error responses instead of raw stack traces if an API call fails.

---

### 4. 👤 Member 4 — Niki (Diagnostic Path & Evaluation Benchmark)
* **Goal**: Deliver the mandatory stretch challenge (Diagnostic $\rightarrow$ 4-Session Revision Path) and measurable evaluation evidence.
* **Key Tasks**:
  1. **Prompt Chaining Pipeline**:
     - Chain Diagnostic output $\rightarrow$ Performance Analysis $\rightarrow$ Weak Topic Detection $\rightarrow$ 4-Session Personalized Revision Plan.
     - Ensure Session 1 focuses on the weakest topic, Session 2 covers prerequisites, Session 3 addresses secondary weak topics, and Session 4 provides mixed retesting.
  2. **Evaluation Suite (`evaluator.py`)**:
     - Execute 12 labelled test cases (valid topics, beginner/intermediate/advanced, off-topic, empty strings, unusual syntax).
     - Report the official metric:
       $$\text{Format Validity Rate} = \frac{\text{Valid Outputs}}{\text{Total Test Cases}} \times 100$$
     - Demonstrate measurable improvement: $V_1\ (70\%) \longrightarrow \text{FINAL}\ (100\%)$.
  3. **Prompt Version History (`prompt_history.csv`)**:
     - Maintain timestamped changelogs tracking iterative prompt refinements.

---

## 🎯 3-Hour Hackathon Presentation Flow

1. **Introduction (1 min — Nikhil)**: Present the core problem (students need guided adaptive learning with weak-topic remediation, not generic chatbots).
2. **Concept Teaching & Level Adaptation (2 min — Devendrasinh)**: Demonstrate **Learn Mode** on `Decorators` at *Beginner* vs *Advanced*.
3. **Guardrails & Safety (1 min — Phani)**: Demonstrate rejection of an off-topic query (e.g., *"What is the weather?"*) and schema validation.
4. **Diagnostic & AI Revision Path (2 min — Niki)**: Complete a 10-question diagnostic, show the weak-topic analysis, and display the personalized 4-session revision plan.
5. **Prompt Engineering & Evaluation (1 min — Team)**: Present the prompt history ($V_1 \rightarrow \text{Final}$) and the **100% Format Validity Rate** on the 12-case evaluation suite.
