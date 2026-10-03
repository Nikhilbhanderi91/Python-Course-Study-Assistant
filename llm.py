import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

from prompts import SYSTEM_PROMPT
from utils import safe_json

load_dotenv()

class LLM:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.api_key:
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str) -> str:
        """
        Generates text using Google Gemini API.
        Handles missing API keys, API errors, and empty responses gracefully.
        """
        if not self.available:
            return "Error: Missing GEMINI_API_KEY. Please configure it in your .env file."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )

            if not response or not response.text:
                return "Error: Received an empty response from Gemini."

            return response.text

        except APIError as e:
            return f"Gemini API Error: {e.message}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generates structured JSON using Gemini with application-level parsing guardrail.
        """
        if not self.available:
            return {
                "status": "error",
                "reason": "MISSING_API_KEY",
                "message": "Missing GEMINI_API_KEY in environment."
            }

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )

            if not response or not response.text:
                return {
                    "status": "error",
                    "reason": "EMPTY_RESPONSE",
                    "message": "Empty response from AI."
                }

            return safe_json(response.text)

        except APIError as e:
            return {
                "status": "error",
                "reason": "API_ERROR",
                "message": f"Gemini API Error: {e.message}"
            }
        except (json.JSONDecodeError, Exception):
            return {
                "status": "error",
                "reason": "INVALID_AI_OUTPUT",
                "message": "The generated response could not be processed. Please try again."
            }
