import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.realtime_rag import RealtimeRAGClient

def main():
    print("Testing DuckDuckGo Scraper fallback...")
    client = RealtimeRAGClient()
    
    query = "Vidya Khobrekar"
    print(f"Querying: '{query}'")
    results = client.fetch_unauthenticated_search(query)
    
    print("\n--- Results ---")
    if not results:
        print("No results returned from scraper.")
    else:
        for i, res in enumerate(results, 1):
            print(f"{i}. Title: {res.get('title')}")
            print(f"   URL: {res.get('url')}")
            print(f"   Snippet: {res.get('snippet')}\n")

if __name__ == "__main__":
    main()
