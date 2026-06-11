import httpx
import urllib.parse

def test_raw_ddg():
    query = "Vidya Khobrekar site:indiankanoon.org OR site:livelaw.in OR site:barandbench.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with httpx.Client(timeout=10, headers=headers, follow_redirects=True) as client:
        resp = client.post("https://html.duckduckgo.com/html/", data={"q": query})
        print(f"Status Code: {resp.status_code}")
        print(f"Response Length: {len(resp.text)} characters")
        print("\nFirst 1000 characters of response:")
        print(resp.text[:1000])
        
        # Check if result__body is in response
        if 'result__body' in resp.text:
            print("\nFound 'result__body' in response!")
            # Count result__body occurrences
            count = resp.text.count('result__body')
            print(f"Occurrences of 'result__body': {count}")
        else:
            print("\n'result__body' NOT found in response!")
            # Check if there are links or titles in another format
            if 'class="result__' in resp.text:
                print("Found other result__ classes!")
            else:
                print("No result__ classes found at all.")

if __name__ == "__main__":
    test_raw_ddg()
