from tools.realtime_rag import RealtimeRAGClient

def test_ddg_vidya():
    print("Querying unauthenticated public web index for real-world legal matters of Smt. Vidya Khobrekar...")
    client = RealtimeRAGClient()
    
    queries = [
        "Vidya Khobrekar Nagpur",
        "Vidya Khobrekar advocate Nagpur",
        "Vidya Khobrekar Bombay High Court",
        "Vidya Khobrekar case"
    ]
    
    for q in queries:
        print(f"\n--- Searching for: '{q}' ---")
        results = client.fetch_unauthenticated_search(q)
        if not results:
            print("No results returned.")
        else:
            for i, res in enumerate(results, 1):
                print(f"{i}. Title: {res['title']}")
                print(f"   URL: {res['url']}")
                print(f"   Snippet: {res['snippet'][:250]}...\n")

if __name__ == "__main__":
    test_ddg_vidya()
