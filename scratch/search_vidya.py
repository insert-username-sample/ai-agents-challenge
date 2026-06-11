import os
from google import genai
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig
from dotenv import load_dotenv
load_dotenv()

def search_vidya():
    print("Searching for Vidya Khobrekar cases and legal references via Google Search Grounding...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found in environment.")
        return
        
    client = genai.Client(api_key=api_key)
    google_search_tool = Tool(google_search=GoogleSearch())
    
    try:
        # Search for Vidya Khobrekar in legal databases and courts
        prompt = (
            "Find all court cases, judgments, orders, or legal proceedings in India "
            "involving 'Vidya Khobrekar' or related to her name (e.g. Bombay High Court, Maharashtra, Nagpur, etc.)."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(tools=[google_search_tool]),
        )
        
        print("\n--- Search Response ---")
        print(response.text)
        
        candidate = response.candidates[0] if response.candidates else None
        if candidate and hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            meta = candidate.grounding_metadata
            chunks = getattr(meta, 'grounding_chunks', []) or []
            print("\n--- Grounded Sources ---")
            for chunk in chunks:
                if hasattr(chunk, 'web') and chunk.web:
                    print(f"- Title: {chunk.web.title}")
                    print(f"  URL: {chunk.web.uri}")
        else:
            print("\nNo grounding metadata found.")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    search_vidya()
