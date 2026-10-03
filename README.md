# Python Course Study Assistant — Hackathon Prototype

A prompt-based study assistant for the hackathon problem "Python Course Study Assistant".

## Features
- Explains Python concepts at Beginner / Intermediate / Advanced level.
- Generates a quiz with answer key.
- Generates flashcards at the chosen difficulty.
- 5-item accuracy check.
- Mandatory stretch challenge: diagnostic quiz -> weak-topic analysis -> personalized learning path + revision plan.
- Two prompting techniques shown side-by-side:
  1. Zero/Few-shot structured prompting
  2. Chain-of-thought-style decomposition without exposing hidden reasoning; the model is asked for concise step checks instead.
- Guardrails for invalid input, off-topic requests, and invalid model output.
- Timestamped prompt history saved to `prompt_history.csv`.
- Evaluation tab with 10+ labeled cases and one metric: valid/accurate item rate.
- Includes a deterministic Demo Mode so the UI can run without an API key.

## Run
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# or: cp .env.example .env

streamlit run app.py
```

Put your API key in `.env` for LLM mode.

## 3-hour hackathon demo flow
1. Enter `lists`, difficulty `Beginner`.
2. Show explanation + quiz + flashcards.
3. Change to `Advanced` to demonstrate level adaptation.
4. Open "Prompting comparison" and show Technique A vs Technique B.
5. Run the diagnostic quiz and show weak-topic learning path.
6. Open "Evaluation" and show 10+ cases and the metric.
7. Enter an off-topic request such as "Write me a poem" and show the guardrail.
8. Show `prompt_history.csv` with timestamps.

## Suggested metric
**Valid Item Rate = valid generated quiz/flashcard items ÷ total requested items × 100**

For the evaluation set, also report:
- first version valid item rate
- final version valid item rate
- improvement in percentage points
