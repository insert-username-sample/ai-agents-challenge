import os
from google import genai
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig
from dotenv import load_dotenv
load_dotenv()

def test_grounding():
    print("Testing dynamic Google Search Grounding with new google-genai SDK...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment.")
        return
        
    client = genai.Client(api_key=api_key)
    
    try:
        google_search_tool = Tool(google_search=GoogleSearch())
        
        prompt = "Vidya Khobrekar"
        print(f"Prompt: '{prompt}'")
        
        # Use gemini-2.5-flash which is widely supported for search grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(
                tools=[google_search_tool],
            ),
        )
        
        print("\n--- Grounded Response ---")
        print(response.text)
        
        # Inspect the grounding metadata
        candidate = response.candidates[0]
        print(f"\nCandidate structure: {type(candidate)}")
        print(f"Content: {candidate.content}")
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            meta = candidate.grounding_metadata
            print("\n--- Live Web Search Queries ---")
            print(meta.web_search_queries)
            
            print("\n--- Live Verified Sources ---")
            chunks = getattr(meta, 'grounding_chunks', [])
            if chunks:
                for chunk in chunks:
                    if hasattr(chunk, 'web') and chunk.web:
                        print(f"- Title: {chunk.web.title}")
                        print(f"  URL: {chunk.web.uri}")
            else:
                print("No grounding chunks returned.")
        else:
            print("\nNo grounding metadata returned.")
            
    except Exception as e:
        print(f"Gemini Grounding request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grounding()
