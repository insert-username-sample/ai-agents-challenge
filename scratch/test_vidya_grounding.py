import os
from google import genai
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig
from dotenv import load_dotenv
load_dotenv()

def test_vidya_grounding():
    print("Testing Vidya Khobrekar grounding queries...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment.")
        return
        
    client = genai.Client(api_key=api_key)
    google_search_tool = Tool(google_search=GoogleSearch())
    
    queries = [
        "Vidya Khobrekar single mother Gondia caste case",
        "Vidya alias Vidhyabai d/o late Shri Digambarrao Khobrekar & Anr. v. State of Maharashtra & Ors.",
        "Vidya Khobrekar Gondia Mahar caste certificate"
    ]
    
    for q in queries:
        print(f"\n==================================================")
        print(f"QUERY: '{q}'")
        print(f"==================================================")
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Find the actual court order or case details for: {q}. Provide a concise summary of the case facts, the legal issue (single mother, Mahar caste, SDO Gondia), and the court's judgment.",
                config=GenerateContentConfig(tools=[google_search_tool]),
            )
            print("\nResponse:")
            print(response.text)
            
            candidate = response.candidates[0] if response.candidates else None
            if candidate and hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                meta = candidate.grounding_metadata
                print("\nLive Search Queries:")
                print(meta.web_search_queries)
                print("\nLive Grounded Sources:")
                chunks = getattr(meta, 'grounding_chunks', [])
                for chunk in chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        print(f"- {chunk.web.title}: {chunk.web.uri}")
            else:
                print("No grounding metadata returned.")
        except Exception as e:
            print(f"Query failed: {e}")

if __name__ == "__main__":
    test_vidya_grounding()
