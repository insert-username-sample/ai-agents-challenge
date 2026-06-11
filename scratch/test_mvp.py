import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "mcps")))
from common_browser import BrowserBridge

async def test_chatgpt(bridge):
    print("\n=== Testing ChatGPT Web ===")
    try:
        content = await bridge.interact(
            url="https://chatgpt.com",
            wait_selector="article div.markdown",
            input_selector="#prompt-textarea",
            prompt="Hello ChatGPT, reply with 'ChatGPT_Success' only."
        )
        print("ChatGPT Response:\n", content)
    except Exception as e:
        print("ChatGPT Error:", e)

async def test_gemini(bridge):
    print("\n=== Testing Gemini Web ===")
    try:
        content = await bridge.interact(
            url="https://gemini.google.com/app",
            wait_selector="message-content",
            input_selector="div[role='textbox']",
            prompt="Hello Gemini, reply with 'Gemini_Success' only."
        )
        print("Gemini Response:\n", content)
    except Exception as e:
        print("Gemini Error:", e)

async def test_notebooklm(bridge, p):
    print("\n=== Testing NotebookLM Web ===")
    try:
        # Search contexts to find any active notebook page
        from common_browser import connect_to_chrome
        browser = await connect_to_chrome(p)
        notebook_id = None
        for context in browser.contexts:
            for page in context.pages:
                if "notebooklm.google.com/notebook/" in page.url:
                    parts = page.url.split("/notebook/")
                    if len(parts) > 1:
                        notebook_id = parts[1].split("/")[0].split("?")[0]
                        print(f"Found active NotebookLM notebook ID: {notebook_id}")
                        break
            if notebook_id:
                break
        
        if not notebook_id:
            print("No active NotebookLM notebook tab found. Skipping NotebookLM prompt test.")
            return
        
        content = await bridge.interact(
            url=f"https://notebooklm.google.com/notebook/{notebook_id}",
            wait_selector=".chat-response-class, div[role='log']",
            input_selector="textarea[placeholder*='Ask a question']",
            prompt="Hello NotebookLM, reply with 'NotebookLM_Success' only."
        )
        print("NotebookLM Response:\n", content)
    except Exception as e:
        print("NotebookLM Error:", e)

async def main():
    bridge = BrowserBridge("test")
    async with async_playwright() as p:
        # Check connection
        try:
            from common_browser import connect_to_chrome
            browser = await connect_to_chrome(p)
            print("Successfully verified connection to Chrome session.")
        except Exception as e:
            print("Chrome connection check failed:", e)
            return

        # Run tests
        await test_chatgpt(bridge)
        await test_gemini(bridge)
        await test_notebooklm(bridge, p)

if __name__ == "__main__":
    asyncio.run(main())
