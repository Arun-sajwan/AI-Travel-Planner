import os
import json

import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

client = genai.Client(
    api_key=api_key
)

def create_travel_plan(prompt):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            text = response.text.strip()

            # Remove Markdown code fences
            if text.startswith("```json"):
                text = text[7:]

            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            return json.loads(text)


        except Exception as e:

            error_text = str(e).lower()

            if (
                "429" in error_text
                or "quota" in error_text
                or "rate limit" in error_text
            ):
                raise RuntimeError(
                    "The API key token limit has reached. "
                    "Please try again later."
                )

            if (
                "503" in error_text
                or "temporarily busy" in error_text
                or "service unavailable" in error_text
            ):
                raise RuntimeError(
                    "Gemini is temporarily busy. "
                    "Please try again in a few moments."
                )

            raise
