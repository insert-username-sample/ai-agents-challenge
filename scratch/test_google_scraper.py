import httpx
import re
import urllib.parse

def test_google_scrape():
    print("Testing unauthenticated Google Search scraper...")
    query = "Vidya Khobrekar"
    search_query = f"{query} site:indiankanoon.org OR site:livelaw.in OR site:barandbench.com OR site:casemine.com"
    
    url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        with httpx.Client(timeout=10, headers=headers, follow_redirects=True) as client:
            resp = client.get(url)
            print(f"Status Code: {resp.status_code}")
            
            # Print page title to see if blocked by captcha
            title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
            if title_match:
                print(f"Page Title: {title_match.group(1)}")
            
            # Find all absolute links to our target domains in the HTML
            domains = ["indiankanoon.org", "livelaw.in", "barandbench.com", "casemine.com", "sci.gov.in", "ecourts.gov.in"]
            all_found = []
            for d in domains:
                matches = re.findall(rf'href="([^"]*{d}[^"]*)"', resp.text)
                if matches:
                    print(f"Domain '{d}' matches:")
                    for m in matches[:3]:
                        print(f"  - {m}")
                        all_found.append(m)
            
            print(f"\nTotal matches found: {len(all_found)}")
            
            # Print a snippet of the page text to inspect
            clean_text = re.sub(r"<[^>]+>", " ", resp.text)
            clean_text = re.sub(r"\s+", " ", clean_text)
            print("\nSnippet of text on the page:")
            print(clean_text[:600] + "...")

            # Check if page contains typical Google search result markers (e.g. href="/url?q=" or result class)
            # Standard Google search result links usually match: <a href="/url?q=https://...
            links = re.findall(r'href="/url\?q=(https?://[^&"]+)', resp.text)
            print(f"Found {len(links)} links:")
            for link in links[:5]:
                decoded = urllib.parse.unquote(link)
                print(f"- {decoded}")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_google_scrape()
