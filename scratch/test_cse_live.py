import os
from dotenv import load_dotenv
load_dotenv()

from tools.realtime_rag import RealtimeRAGClient

def main():
    print("Testing Real-Time RAG Search Client...")
    print(f"GOOGLE_CSE_CX: {os.getenv('GOOGLE_CSE_CX')}")
    print(f"GOOGLE_CSE_KEY starts with: {os.getenv('GOOGLE_CSE_KEY')[:8] if os.getenv('GOOGLE_CSE_KEY') else None}...")
    
    client = RealtimeRAGClient()
    
    # Test our live RAG search pipeline
    query = "Vidya Khobrekar"
    print(f"\nQuerying: '{query}'")
    results = client.search_general(query)
    
    print("\n--- Real-Time RAG Results ---")
    if not results:
        print("No results returned.")
    else:
        for i, res in enumerate(results, 1):
            print(f"{i}. Title: {res.get('title')}")
            print(f"   URL: {res.get('url')}")
            print(f"   Source: {res.get('source')}")
            print(f"   Snippet: {res.get('snippet')[:200]}...\n")


if __name__ == "__main__":
    main()
