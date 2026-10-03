import os, json
from dotenv import load_dotenv
from openai import OpenAI
from prompts import SYSTEM_PROMPT
from utils import safe_json

load_dotenv()

class LLM:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def available(self):
        return self.client is not None

    def ask_json(self, prompt):
        if not self.client:
            raise RuntimeError("No API key. Enable Demo Mode or add OPENAI_API_KEY to .env.")
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return safe_json(response.choices[0].message.content)

    def ask_text(self, prompt):
        if not self.client:
            raise RuntimeError("No API key. Enable Demo Mode or add OPENAI_API_KEY to .env.")
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
