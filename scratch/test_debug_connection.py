import asyncio
from playwright.async_api import async_playwright
import os
import subprocess

async def test():
    cdp_url = "http://127.0.0.1:9222"
    async with async_playwright() as p:
        # 1. Try to connect directly
        try:
            print("Trying direct connection...")
            browser = await p.chromium.connect_over_cdp(cdp_url)
            print("Connected directly!")
            return
        except Exception as e:
            print("Direct connection failed:", e)

        # 2. Try to auto-start
        try:
            print("Trying auto-start...")
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            subprocess.Popen([
                chrome_path,
                "--remote-debugging-port=9222",
                "--user-data-dir=C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data",
                "--profile-directory=Profile 1"
            ])
            print("Subprocess spawned.")
            for i in range(12):
                await asyncio.sleep(0.5)
                try:
                    print(f"Retry {i+1} connecting...")
                    browser = await p.chromium.connect_over_cdp(cdp_url)
                    print("Connected on retry!")
                    return
                except Exception as e:
                    print(f"Retry {i+1} failed:", e)
        except Exception as e:
            print("Auto-start failed:", e)

if __name__ == "__main__":
    asyncio.run(test())
