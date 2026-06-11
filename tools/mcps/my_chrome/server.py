import os
import sys
import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_browser import connect_to_chrome

mcp = FastMCP("My-Chrome-Browser")

CDP_URL = "http://127.0.0.1:9222"

@mcp.tool()
async def get_active_tab_content() -> str:
    """
    Connects to the user's running Chrome browser via port 9222.
    Returns the URL, title, and visible text content of the currently active tab.
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            contexts = browser.contexts
            if not contexts:
                return "Error: No browser contexts found. Make sure Chrome is running with --remote-debugging-port=9222."
            page = None
            for context in contexts:
                if context.pages:
                    page = context.pages[0]
                    break
            if not page:
                return "Error: No active tabs found."
            url = page.url
            title = await page.title()
            text = await page.evaluate("() => document.body.innerText")
            return f"--- Active Tab ---\nTitle: {title}\nURL: {url}\n\nContent:\n{text[:5000]}"
    except Exception as e:
        return f"Connection failed: {str(e)}\nMake sure Chrome was launched with --remote-debugging-port=9222."

@mcp.tool()
async def get_all_tabs() -> str:
    """
    Lists all open tabs across all browser contexts, including their titles and URLs.
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            contexts = browser.contexts
            if not contexts:
                return "Error: No browser contexts found."
            output = ["--- All Open Tabs ---"]
            tab_index = 1
            for ctx_i, context in enumerate(contexts):
                for page in context.pages:
                    try:
                        title = await page.title()
                        url = page.url
                        output.append(f"[{tab_index}] {title}\n    URL: {url}")
                        tab_index += 1
                    except Exception:
                        output.append(f"[{tab_index}] (Could not read tab)")
                        tab_index += 1
            return "\n".join(output)
    except Exception as e:
        return f"Error listing tabs: {str(e)}"

@mcp.tool()
async def get_tab_content_by_url(url_fragment: str) -> str:
    """
    Finds a tab whose URL contains the given fragment and returns its content.
    :param url_fragment: A partial URL string to match (e.g. 'github.com', 'notion.so').
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                for page in context.pages:
                    if url_fragment.lower() in page.url.lower():
                        title = await page.title()
                        text = await page.evaluate("() => document.body.innerText")
                        return f"--- Tab Found ---\nTitle: {title}\nURL: {page.url}\n\nContent:\n{text[:5000]}"
            return f"No tab found matching URL fragment: '{url_fragment}'"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def open_url_in_browser(url: str) -> str:
    """
    Opens a URL in a new tab in the user's connected Chrome browser.
    :param url: The full URL to open (must start with http:// or https://).
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        return "Error: URL must start with http:// or https://"
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            contexts = browser.contexts
            if not contexts:
                return "Error: No browser contexts found."
            context = contexts[0]
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            title = await page.title()
            return f"Opened new tab: {title}\nURL: {url}"
    except Exception as e:
        return f"Error opening URL: {str(e)}"

@mcp.tool()
async def close_tab_by_url(url_fragment: str) -> str:
    """
    Closes the first tab whose URL contains the given fragment.
    :param url_fragment: A partial URL string to match (e.g. 'reddit.com').
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                for page in context.pages:
                    if url_fragment.lower() in page.url.lower():
                        url = page.url
                        await page.close()
                        return f"Closed tab: {url}"
            return f"No tab found matching: '{url_fragment}'"
    except Exception as e:
        return f"Error closing tab: {str(e)}"

@mcp.tool()
async def click_element_on_active_tab(css_selector: str) -> str:
    """
    Clicks a DOM element on the currently active tab using a CSS selector.
    :param css_selector: A valid CSS selector (e.g. 'button#submit', 'a.nav-link').
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                if context.pages:
                    page = context.pages[0]
                    await page.wait_for_selector(css_selector, timeout=10000)
                    await page.click(css_selector)
                    return f"Clicked element: {css_selector}"
            return "Error: No active tab found."
    except Exception as e:
        return f"Error clicking element: {str(e)}"

@mcp.tool()
async def type_text_on_active_tab(css_selector: str, text: str, press_enter: bool = False) -> str:
    """
    Types text into a focused input field on the active tab.
    :param css_selector: CSS selector for the input field.
    :param text: The text to type.
    :param press_enter: Whether to press Enter after typing.
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                if context.pages:
                    page = context.pages[0]
                    await page.wait_for_selector(css_selector, timeout=10000)
                    await page.fill(css_selector, text)
                    if press_enter:
                        await page.keyboard.press("Enter")
                    return f"Typed text into: {css_selector}" + (" and pressed Enter." if press_enter else ".")
            return "Error: No active tab found."
    except Exception as e:
        return f"Error typing text: {str(e)}"

@mcp.tool()
async def take_screenshot_of_active_tab(save_path: str = "screenshot.png") -> str:
    """
    Takes a screenshot of the currently active tab and saves it to a local file path.
    :param save_path: Absolute or relative file path to save the PNG screenshot.
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                if context.pages:
                    page = context.pages[0]
                    await page.screenshot(path=save_path, full_page=False)
                    return f"Screenshot saved to: {save_path}"
            return "Error: No active tab found."
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

@mcp.tool()
async def run_js_on_active_tab(javascript_code: str) -> str:
    """
    Executes arbitrary JavaScript on the currently active tab and returns the result.
    :param javascript_code: JavaScript expression or function body to evaluate.
    """
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                if context.pages:
                    page = context.pages[0]
                    result = await page.evaluate(javascript_code)
                    return f"JS Result: {result}"
            return "Error: No active tab found."
    except Exception as e:
        return f"Error executing JavaScript: {str(e)}"

@mcp.tool()
async def scroll_active_tab(direction: str = "down", amount: int = 500) -> str:
    """
    Scrolls the active tab up or down by a pixel amount.
    :param direction: 'up' or 'down'.
    :param amount: Number of pixels to scroll.
    """
    if direction not in ("up", "down"):
        return "Error: direction must be 'up' or 'down'."
    try:
        async with async_playwright() as p:
            browser = await connect_to_chrome(p, CDP_URL)
            for context in browser.contexts:
                if context.pages:
                    page = context.pages[0]
                    scroll_y = amount if direction == "down" else -amount
                    await page.evaluate(f"window.scrollBy(0, {scroll_y})")
                    return f"Scrolled {direction} by {amount}px."
            return "Error: No active tab found."
    except Exception as e:
        return f"Error scrolling: {str(e)}"

if __name__ == "__main__":
    mcp.run()
