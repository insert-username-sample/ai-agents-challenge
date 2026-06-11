import os
from google import genai
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig
from dotenv import load_dotenv
load_dotenv()

def search_petitioner_cases():
    print("Searching for real-world court cases of Smt. Vidya Khobrekar (Petitioner-in-Person)...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found in environment.")
        return
        
    client = genai.Client(api_key=api_key)
    google_search_tool = Tool(google_search=GoogleSearch())
    
    # Search for her as petitioner-in-person in Nagpur/Bombay High Court
    queries = [
        '"Vidya alias Vidhyabai" Gondia',
        '"Vidya Khobrekar" Gondia "caste"',
        '"Vidya Khobrekar" single mother',
        '"Vidya Khobrekar" Nagpur Bench "caste certificate"',
        '"Vidya Khobrekar" petitioner-in-person'
    ]
    
    try:
        for q in queries:
            print(f"\n--- Querying: {q} ---")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    f"Find all real court judgments and orders from Bombay High Court (Nagpur Bench) "
                    f"where the petitioner is listed as: {q}. "
                    "Extract the real case names, citations, and the legal dispute involved."
                ),
                config=GenerateContentConfig(tools=[google_search_tool]),
            )
            print(response.text)
            
            candidate = response.candidates[0] if response.candidates else None
            if candidate and hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                meta = candidate.grounding_metadata
                chunks = getattr(meta, 'grounding_chunks', []) or []
                print("\nSources found:")
                for chunk in chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        print(f"- {chunk.web.title}: {chunk.web.uri}")
            else:
                print("No active metadata.")
                
    except Exception as e:
        print(f"Grounding search failed: {e}")

if __name__ == "__main__":
    search_petitioner_cases()
