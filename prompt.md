# 👥 Python Pulse — Team Work Allocation & Responsibilities

**Project:** Python Course Study Assistant (`PYTHON PULSE`)  
**Hackathon Target:** 3-Hour AI Education Prototype  
**Architecture:** Google Gemini API (`google-genai` SDK) + Streamlit UI + Dual Guardrails + Evaluation Benchmark  

---

## 📌 Team Roster & Module Ownership

| Member | Name | Core Area / Ownership | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Nikhil** | **Team Lead & UI / LLM Architecture** | • Google Gemini API integration (`llm.py`)<br>• Streamlit app orchestration & Step-by-Step Flow (`app.py`)<br>• Git Repository management & lead presentation |
| **Member 2** | **Devendrasinh** | **Prompt Engineering & Adaptation** | • Master system prompt & role prompting (`prompts.py`)<br>• Few-shot exemplars & level adaptation (Beginner / Intermediate / Advanced)<br>• Technique A (Few-Shot) vs Technique B (Decomposition) comparison |
| **Member 3** | **Phani** | **Guardrails, Security & Analytics** | • Dual-layer input & output guardrails (`utils.py`)<br>• Off-topic query blocking & strict JSON schema validation<br>• Objective scoring & weak topic detection |
| **Member 4** | **Niki** | **Diagnostic Pipeline & Evaluation** | • 10-question diagnostic assessment & 4-session revision plan (`prompts.py`, `evaluator.py`)<br>• 12-case evaluation benchmark with **Format Validity Rate** ($V_1: 70\% \rightarrow \text{Final}: 100\%$)<br>• Timestamped prompt changelog (`prompt_history.csv`) |

---

## 📋 Detailed Member Task Breakdown

### 1. 👤 Member 1: Nikhil (Team Lead & UI / Core LLM Integration)
* **Core Responsibilities:**
  1. **Google Gemini Client Integration (`llm.py`)**:
     - Maintain `genai.Client(api_key=...)` using `gemini-2.5-flash`.
     - Implement clean JSON generation mode with temperature control and fallback handling.
  2. **Streamlit App Orchestration (`app.py`)**:
     - Connect the 6-step guided learning path:
       $$\text{① Topic} \longrightarrow \text{② Learn} \longrightarrow \text{③ Quiz} \longrightarrow \text{④ Flashcards} \longrightarrow \text{⑤ Diagnostic} \longrightarrow \text{⑥ Revision}$$
     - Maintain an intuitive dark theme and visual journey tracker.
  3. **Repository Management & Lead Presentation**:
     - Manage GitHub commits, version control, and present the live demo.

---

### 2. 👤 Member 2: Devendrasinh (Prompt Engineering & Adaptability)
* **Core Responsibilities:**
  1. **System & Role Prompting (`prompts.py`)**:
     - Implement the expert Python educator persona.
     - Enforce non-hallucination constraints and curriculum boundaries.
  2. **Difficulty Adaptation (Beginner / Intermediate / Advanced)**:
     - **Beginner**: Simple definitions, syntax templates, line-by-line breakdown, common beginner mistakes.
     - **Intermediate**: Practical applications, best practices, debugging scenarios.
     - **Advanced**: Internal runtime behavior, performance trade-offs, edge cases.
  3. **Technique Comparison**:
     - Benchmark **Technique A** (Few-Shot Role Prompting) vs **Technique B** (Decomposition + Constraints).

---

### 3. 👤 Member 3: Phani (Guardrails, Validation & Analytics)
* **Core Responsibilities:**
  1. **Dual Guardrail Implementation (`utils.py`)**:
     - **Input Validation**: Block off-topic queries (weather, politics, sports), empty strings, and long inputs (>300 chars).
     - **Output Validation**: Enforce exact JSON schemas without markdown fences.
  2. **Performance Scoring & Analytics**:
     - Calculate genuine performance without fabricating student data:
       - **Strong**: $\ge 80\%$
       - **Developing**: $60\% - 79\%$
       - **Weak**: $< 60\%$
  3. **Error Handling**:
     - Provide clean user-facing error messages instead of raw stack traces.

---

### 4. 👤 Member 4: Niki (Diagnostic Path & Evaluation Benchmark)
* **Core Responsibilities:**
  1. **Diagnostic & Prompt Chaining Pipeline**:
     - Multi-stage chaining: `Diagnostic Assessment -> Weak Topic Detection -> 4-Session Personalized Revision Plan`.
     - Prioritize weak topics (<60%) in Session 1 and Session 2.
  2. **Evaluation Suite (`evaluator.py`)**:
     - Run 12 labelled test cases across valid topics, beginner/intermediate/advanced levels, and edge cases.
     - Compute the official metric:
       $$\text{Format Validity Rate} = \frac{\text{Valid Outputs}}{\text{Total Test Cases}} \times 100$$
     - Demonstrate $V_1\ (70\%) \longrightarrow \text{FINAL}\ (100\%)$ improvement.
  3. **Timestamped Prompt Version History (`prompt_history.csv`)**:
     - Track all prompt iterations and observed results across development.

---

## ⏱️ 3-Hour Hackathon Presentation Roadmap

1. **Introduction (1 min — Nikhil)**: The problem, solution, and the step-by-step guided journey.
2. **Concept Teaching & Level Adaptation (2 min — Devendrasinh)**: Live Learn Mode demo with difficulty adaptation.
3. **Guardrails & Safety (1 min — Phani)**: Live test of off-topic rejection and output validation.
4. **Diagnostic & AI Revision Path (2 min — Niki)**: 10-question diagnostic quiz, weak-topic analytics, and 4-session revision plan.
5. **Evaluation Benchmark (1 min — Team)**: 12-case test suite report with **100% Format Validity Rate**.
