import os
import sys
import subprocess
import asyncio
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "mcps")))
from common_browser import BrowserBridge

async def main():
    # 1. Kill Chrome processes to release files and port locks
    print("Terminating existing Chrome processes...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    except Exception as e:
        print("Error terminating Chrome:", e)
    
    await asyncio.sleep(2.0)
    
    # 2. Use BrowserBridge to start Chrome and navigate
    bridge = BrowserBridge("test")
    print("Attempting to launch Chrome with remote debugging and load ChatGPT...")
    async with async_playwright() as p:
        try:
            browser, page = await bridge.get_page(p, "https://chatgpt.com")
            print("Connection successful!")
            print("URL:", page.url)
            print("Title:", await page.title())
        except Exception as e:
            print("Connection failed:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
