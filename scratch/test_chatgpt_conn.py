import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "mcps")))
from common_browser import BrowserBridge

async def main():
    bridge = BrowserBridge("test")
    url = "https://chatgpt.com/c/6a21d311-065c-8324-9e52-fd0b04817966"
    print(f"Connecting to user browser and loading {url}...")
    try:
        res = await bridge.interact(url=url, wait_selector="article div.markdown")
        print("\n--- Interaction Successful! Content Snippet: ---")
        print(res[:1500])
        print("-------------------------------------------------")
    except Exception as e:
        print(f"Error during test execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
