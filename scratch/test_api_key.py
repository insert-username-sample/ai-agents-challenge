import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"API Key found: {api_key[:10]}...{api_key[-5:]}")
else:
    print("API Key not found.")

try:
    client = genai.Client(api_key=api_key)
    print("Sending test request to gemini-3.5-flash...")
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Hello! Confirm you are running as Gemini 3.5 Flash."
    )
    print(">>> SUCCESS!")
    print(response.text)
except Exception as e:
    print(">>> FAILED!")
    print(e)
