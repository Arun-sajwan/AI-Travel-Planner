import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai


# Load local .env file
load_dotenv()


def get_api_key():
    """
    Get Gemini API key.

    On Streamlit Cloud:
        read from st.secrets

    Locally:
        read from .env
    """

    # Try Streamlit Secrets first
    try:
        api_key = st.secrets["GEMINI_API_KEY"]

        if api_key:
            return api_key

    except (KeyError, FileNotFoundError):
        pass

    # Fall back to local .env
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Add it to your local .env file or "
        "Streamlit Cloud Secrets."
    )


# Get API key
api_key = get_api_key()


# Create Gemini client
client = genai.Client(
    api_key=api_key
)


def create_travel_plan(prompt):
    """
    Send the travel planning prompt to Gemini
    and return the response as a Python dictionary.
    """

    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    text = response.output_text.strip()

    # Remove Markdown code fences
    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Convert Gemini JSON into Python dictionary
    return json.loads(text)