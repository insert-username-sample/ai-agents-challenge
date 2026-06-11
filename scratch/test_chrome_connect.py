import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "mcps")))
from common_browser import BrowserBridge

async def main():
    bridge = BrowserBridge("test")
    print("Attempting to connect to ChatGPT...")
    async with async_playwright() as p:
        try:
            browser, page = await bridge.get_page(p, "https://chatgpt.com")
            print("Successfully got page!")
            print("Initial URL:", page.url)
            print("Initial Title:", await page.title())
            print("Waiting 5 seconds for page load...")
            await asyncio.sleep(5.0)
            print("Final URL:", page.url)
            print("Final Title:", await page.title())
        except Exception as e:
            print("Error occurred:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
