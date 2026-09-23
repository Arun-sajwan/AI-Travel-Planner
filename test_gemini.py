import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("Key found:", bool(api_key))

if api_key:
    print("Key prefix:", api_key[:8])
    print("Key length:", len(api_key))

client = genai.Client(
    api_key=api_key
)

response = client.interactions.create(
    model="gemini-3.6-flash",
    input="Reply with exactly: TEST SUCCESS"
)

print(response.output_text)