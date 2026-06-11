import os
import re
import urllib.parse
import httpx
from dotenv import load_dotenv
load_dotenv()

def query_custom_search(query: str):
    print(f"Querying Google Custom Search API for: '{query}'...")
    
    # Use the user's custom developer key
    api_key = "AIzaSyCkjHqYt2_MS0W6Yn4E-WTqk-V_K-PjJkI"
    cx_id = os.getenv("GOOGLE_CSE_CX", "d073459bb5aa24b10")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx_id,
        "q": query,
        "num": 10
    }
    
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params)
            print(f"Status Code: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                print(f"Found {len(items)} results.\n")
                for i, item in enumerate(items, 1):
                    print(f"{i}. Title: {item.get('title')}")
                    print(f"   URL: {item.get('link')}")
                    print(f"   Snippet: {item.get('snippet')}\n")
            else:
                print(f"API Error Response: {resp.text}")
    except Exception as e:
        print(f"Network call failed: {e}")

if __name__ == "__main__":
    # Query for Smt. Vidya Khobrekar cases
    query_custom_search("Vidya Khobrekar Nagpur")
