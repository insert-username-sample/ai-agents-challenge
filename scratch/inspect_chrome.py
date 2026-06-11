import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected to Chromium successfully.")
            for context in browser.contexts:
                for page in context.pages:
                    print(f"Page Title: {await page.title()}")
                    print(f"Page URL: {page.url}")
                    print("-" * 50)
            await browser.close()
        except Exception as e:
            print("Error connecting to Chromium:", e)

if __name__ == "__main__":
    asyncio.run(main())
