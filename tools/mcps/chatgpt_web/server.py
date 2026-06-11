import asyncio
import os
import sys
from typing import Optional, List
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_browser import BrowserBridge

mcp = FastMCP("ChatGPT-Web")
bridge = BrowserBridge("chatgpt_web")

URL = "https://chatgpt.com"
INPUT_SEL = "#prompt-textarea"
WAIT_SEL = "article div.markdown"
ATTACH_SEL = "button[aria-label*='Attach'], button[aria-label*='file'], [class*='attachment'] button"

@mcp.tool()
async def ask_chatgpt_web(prompt: str) -> str:
    """
    Sends a standard text query to chatgpt.com and returns the response.
    :param prompt: The question or instruction to send to ChatGPT.
    """
    try:
        content = await bridge.interact(url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt)
        return f"[ChatGPT Web Response]\n{content}"
    except Exception as e:
        return f"Error executing ChatGPT query: {str(e)}"

@mcp.tool()
async def upload_file_to_chatgpt(file_path: str, prompt: str) -> str:
    """
    Uploads a local file to ChatGPT and sends a prompt about it.
    :param file_path: Absolute local path to the file to upload.
    :param prompt: The query accompanying the file upload.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, 
            prompt=prompt, upload_path=file_path
        )
        return f"[ChatGPT Upload Response]\n{content}"
    except Exception as e:
        return f"Error executing ChatGPT upload: {str(e)}"

@mcp.tool()
async def chatgpt_add_photos_and_files(file_paths: List[str], prompt: Optional[str] = None) -> str:
    """
    Uploads one or multiple local photos/files to ChatGPT and prompts it.
    :param file_paths: List of absolute local file paths.
    :param prompt: Optional prompt to send with the uploads.
    """
    for fp in file_paths:
        if not os.path.exists(fp):
            return f"Error: Local file not found: {fp}"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, 
            prompt=prompt, upload_path=file_paths
        )
        return f"[ChatGPT Upload Response]\n{content}"
    except Exception as e:
        return f"Error executing ChatGPT upload: {str(e)}"

@mcp.tool()
async def chatgpt_recent_files(prompt: Optional[str] = None) -> str:
    """
    Opens the 'Recent files' attachment menu in ChatGPT.
    :param prompt: Optional prompt to send after selecting.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Recent files"])
        if prompt:
            content = await bridge.interact(url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt)
            return f"[ChatGPT Recent Files Response]\n{content}"
        return "[ChatGPT Status]\nRecent files attachment menu clicked."
    except Exception as e:
        return f"Error opening Recent Files: {str(e)}"

@mcp.tool()
async def chatgpt_create_image(prompt: str) -> str:
    """
    Generates an image in ChatGPT using DALL-E 3.
    """
    formatted = f"Create an image of: {prompt}"
    try:
        content = await bridge.interact(url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=formatted)
        return f"[ChatGPT Image Generation]\n{content}"
    except Exception as e:
        return f"Error creating image: {str(e)}"

@mcp.tool()
async def chatgpt_toggle_thinking(prompt: str) -> str:
    """
    Toggles 'Thinking' (reasoning o1/o3) in ChatGPT and submits a query.
    """
    click_selector = "button[aria-label*='Thinking']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[ChatGPT Thinking Response]\n{content}"
    except Exception as e:
        return f"Error triggering ChatGPT Thinking: {str(e)}"

@mcp.tool()
async def chatgpt_toggle_deep_research(prompt: str) -> str:
    """
    Toggles 'Deep Research' in ChatGPT and submits a query.
    """
    click_selector = "button[aria-label*='Deep research']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[ChatGPT Deep Research Response]\n{content}"
    except Exception as e:
        return f"Error triggering ChatGPT Deep Research: {str(e)}"

@mcp.tool()
async def trigger_chatgpt_deep_research(prompt: str) -> str:
    """
    Enables Deep Research mode in ChatGPT and submits a query.
    """
    click_selector = "button[aria-label*='Thinking'], button[aria-label*='Deep research']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[ChatGPT Deep Research Response]\n{content}"
    except Exception as e:
        return f"Error triggering ChatGPT Deep Research: {str(e)}"

@mcp.tool()
async def trigger_chatgpt_canvas(prompt: str) -> str:
    """
    Launches ChatGPT Canvas workspace and submits a coding or writing prompt.
    """
    click_selector = "button[aria-label*='Canvas'], button[aria-label*='OpenAI Platform']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[ChatGPT Canvas Response]\n{content}"
    except Exception as e:
        return f"Error triggering ChatGPT Canvas: {str(e)}"

@mcp.tool()
async def chatgpt_toggle_web_search(prompt: str) -> str:
    """
    Prompts ChatGPT with Web Search explicitly enabled.
    """
    click_selector = "button[aria-label*='Search'], button[aria-label*='Web search']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[ChatGPT Search Response]\n{content}"
    except Exception as e:
        return f"Error triggering ChatGPT Web Search: {str(e)}"

@mcp.tool()
async def chatgpt_download_file(file_name_pattern: Optional[str] = None) -> str:
    """
    Triggers download of the latest generated file/image in ChatGPT and relocates it to the project downloads workspace.
    """
    click_selector = "button[aria-label*='Download'], a[download], [class*='download'] button"
    try:
        await bridge.click_and_wait(url=URL, click_selector=click_selector, wait_ms=8000)
        status = bridge.move_latest_download(project_name="ai agents challenge", file_pattern=file_name_pattern)
        return f"[ChatGPT Download Status]\n{status}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"

@mcp.tool()
async def chatgpt_download_multiple_files(file_name_patterns: List[str]) -> str:
    """
    Triggers download of multiple files and moves them to the workspace downloads folder.
    """
    click_selector = "button[aria-label*='Download'], a[download], [class*='download'] button"
    try:
        await bridge.click_and_wait(url=URL, click_selector=click_selector, wait_ms=5000)
        status = bridge.move_multiple_downloads(project_name="ai agents challenge", count=len(file_name_patterns))
        return f"[ChatGPT Download Status]\n{status}"
    except Exception as e:
        return f"Error executing multiple downloads: {str(e)}"

@mcp.tool()
async def chatgpt_custom_gpt(gpt_url: str, prompt: str) -> str:
    """
    Interacts with a specific custom GPT using its URL.
    :param gpt_url: The full URL to the custom GPT.
    :param prompt: The query to send.
    """
    if not gpt_url.startswith("https://chatgpt.com/g/"):
        return "Error: Invalid Custom GPT URL. Must start with https://chatgpt.com/g/"
    try:
        content = await bridge.interact(
            url=gpt_url, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Custom GPT Response]\n{content}"
    except Exception as e:
        return f"Error executing Custom GPT: {str(e)}"

@mcp.tool()
async def chatgpt_get_conversations() -> str:
    """
    Retrieves the list of recent conversations from the ChatGPT sidebar.
    """
    selector = "nav a[href*='/c/']"
    try:
        results = await bridge.scrape_links_and_text(url=URL, selector=selector)
        if not results:
            return "No recent conversations found or sidebar is hidden."
        output = ["--- Recent ChatGPT Conversations ---"]
        for res in results:
            text = res["text"].replace("\n", " ").strip()
            href = res["href"]
            output.append(f"- {text} (URL: https://chatgpt.com{href})")
        return "\n".join(output)
    except Exception as e:
        return f"Error retrieving ChatGPT conversations: {str(e)}"

@mcp.tool()
async def chatgpt_open_conversation(conversation_url: str) -> str:
    """
    Opens a specific ChatGPT conversation by its URL and returns its content.
    :param conversation_url: Full ChatGPT conversation URL (https://chatgpt.com/c/...).
    """
    if not conversation_url.startswith("https://chatgpt.com/c/"):
        return "Error: Invalid conversation URL. Must start with https://chatgpt.com/c/"
    try:
        content = await bridge.interact(
            url=conversation_url, wait_selector=WAIT_SEL
        )
        return f"[ChatGPT Conversation Content]\n{content}"
    except Exception as e:
        return f"Error opening conversation: {str(e)}"

@mcp.tool()
async def chatgpt_new_conversation() -> str:
    """
    Navigates ChatGPT to a fresh new conversation (blank chat).
    """
    try:
        from common_browser import connect_to_chrome
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await connect_to_chrome(p)
            for context in browser.contexts:
                for page in context.pages:
                    if "chatgpt.com" in page.url:
                        await page.goto("https://chatgpt.com", wait_until="domcontentloaded")
                        return "Navigated to new ChatGPT conversation."
            return "No ChatGPT tab found. Open chatgpt.com first."
    except Exception as e:
        return f"Error starting new conversation: {str(e)}"

if __name__ == "__main__":
    mcp.run()
