import asyncio
from playwright.async_api import async_playwright
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "mcps")))
from common_browser import connect_to_chrome

async def main():
    async with async_playwright() as p:
        try:
            browser = await connect_to_chrome(p)
            print("Successfully connected over CDP!")
            for i, context in enumerate(browser.contexts):
                print(f"Context {i}:")
                for j, page in enumerate(context.pages):
                    print(f"  Page {j}: URL={page.url} Title={await page.title()}")
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
