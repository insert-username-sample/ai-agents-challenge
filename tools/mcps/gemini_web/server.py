import asyncio
import os
import sys
from typing import Optional, List
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_browser import BrowserBridge

mcp = FastMCP("Gemini-Web")
bridge = BrowserBridge("gemini_web")

URL = "https://gemini.google.com/app"
INPUT_SEL = "div[role='textbox']"
WAIT_SEL = "message-content"
ATTACH_SEL = "button[aria-label*='uploads'], button[aria-label*='Add'], button[aria-label*='menu'], button[aria-label*='Attach'], [class*='attachment'] button"

@mcp.tool()
async def ask_gemini_web(prompt: str) -> str:
    """
    Sends a standard query to gemini.google.com.
    """
    try:
        content = await bridge.interact(url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt)
        return f"[Gemini Web Response]\n{content}"
    except Exception as e:
        return f"Error executing Gemini query: {str(e)}"

@mcp.tool()
async def upload_file_to_gemini(file_path: str, prompt: str) -> str:
    """
    Uploads a local file to Gemini Web and submits a prompt about it.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, 
            prompt=prompt, upload_path=file_path
        )
        return f"[Gemini Upload Response]\n{content}"
    except Exception as e:
        return f"Error executing Gemini upload: {str(e)}"

@mcp.tool()
async def gemini_upload_files(file_paths: List[str], prompt: Optional[str] = None) -> str:
    """
    Uploads one or multiple local documents/files to Gemini and prompts it.
    """
    for fp in file_paths:
        if not os.path.exists(fp):
            return f"Error: Local file not found: {fp}"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, 
            prompt=prompt, upload_path=file_paths
        )
        return f"[Gemini Upload Response]\n{content}"
    except Exception as e:
        return f"Error executing Gemini upload: {str(e)}"

@mcp.tool()
async def gemini_add_from_drive(drive_file_name: str, prompt: Optional[str] = None) -> str:
    """
    Selects a file from Google Drive to add to the Gemini conversation.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Add from Drive"])
        formatted = f"Locate and select the Google Drive file '{drive_file_name}'. {prompt or ''}"
        content = await bridge.interact(url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=formatted)
        return f"[Gemini Drive Response]\n{content}"
    except Exception as e:
        return f"Error adding Google Drive file: {str(e)}"

@mcp.tool()
async def gemini_upload_photos(file_paths: List[str], prompt: Optional[str] = None) -> str:
    """
    Uploads photos to Gemini via the 'More uploads > Photos' menu.
    """
    for fp in file_paths:
        if not os.path.exists(fp):
            return f"Error: Local file not found: {fp}"
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More uploads", "Photos"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt, upload_path=file_paths
        )
        return f"[Gemini Photos Response]\n{content}"
    except Exception as e:
        return f"Error uploading photos: {str(e)}"

@mcp.tool()
async def gemini_upload_avatar(file_path: str, prompt: Optional[str] = None) -> str:
    """
    Uploads an avatar file to Gemini via the 'More uploads > Avatar' menu.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More uploads", "Avatar"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt, upload_path=file_path
        )
        return f"[Gemini Avatar Response]\n{content}"
    except Exception as e:
        return f"Error uploading avatar: {str(e)}"

@mcp.tool()
async def gemini_import_code(file_path: str, prompt: Optional[str] = None) -> str:
    """
    Imports a local code file to Gemini via the 'More uploads > Import code' menu.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More uploads", "Import code"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt, upload_path=file_path
        )
        return f"[Gemini Imported Code Response]\n{content}"
    except Exception as e:
        return f"Error importing code: {str(e)}"

@mcp.tool()
async def gemini_upload_notebooks(file_path: str, prompt: Optional[str] = None) -> str:
    """
    Uploads a notebook configuration or script to Gemini via the 'More uploads > Notebooks' menu.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More uploads", "Notebooks"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt, upload_path=file_path
        )
        return f"[Gemini Uploaded Notebooks Response]\n{content}"
    except Exception as e:
        return f"Error uploading notebook: {str(e)}"

@mcp.tool()
async def gemini_create_image(prompt: str) -> str:
    """
    Generates an image in Gemini via the 'Create image' menu option.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Create image"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Image Creation]\n{content}"
    except Exception as e:
        return f"Error creating image: {str(e)}"

@mcp.tool()
async def gemini_create_video(prompt: str) -> str:
    """
    Generates a video in Gemini via the 'Create video' menu option.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Create video"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Video Creation]\n{content}"
    except Exception as e:
        return f"Error creating video: {str(e)}"

@mcp.tool()
async def gemini_canvas(prompt: str) -> str:
    """
    Launches Gemini Canvas writing/coding workspace via the menu option.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Canvas"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Canvas Response]\n{content}"
    except Exception as e:
        return f"Error opening Gemini Canvas: {str(e)}"

@mcp.tool()
async def trigger_gemini_canvas(prompt: str) -> str:
    """
    Launches Gemini Canvas workspace and submits a coding or document prompt.
    """
    click_selector = "button[aria-label*='Canvas']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[Gemini Canvas Response]\n{content}"
    except Exception as e:
        return f"Error triggering Gemini Canvas: {str(e)}"

@mcp.tool()
async def gemini_deep_research(prompt: str) -> str:
    """
    Runs a query in Gemini Deep Research mode via the menu option.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Deep research"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Deep Research Response]\n{content}"
    except Exception as e:
        return f"Error triggering Deep Research: {str(e)}"

@mcp.tool()
async def trigger_gemini_deep_research(prompt: str) -> str:
    """
    Enables Deep Research mode in Gemini and submits a query.
    """
    click_selector = "button[aria-label*='Deep research'], [class*='deep-research']"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL,
            prompt=prompt, click_selector=click_selector
        )
        return f"[Gemini Deep Research Response]\n{content}"
    except Exception as e:
        return f"Error triggering Gemini Deep Research: {str(e)}"

@mcp.tool()
async def gemini_create_music(prompt: str) -> str:
    """
    Generates music in Gemini via the 'Create music' menu option.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["Create music"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Music Response]\n{content}"
    except Exception as e:
        return f"Error generating music: {str(e)}"

@mcp.tool()
async def gemini_guided_learning(prompt: str) -> str:
    """
    Triggers Guided Learning study assistance via the 'More tools > Guided learning' menu path.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More tools", "Guided learning"])
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gemini Guided Learning Response]\n{content}"
    except Exception as e:
        return f"Error opening Guided Learning: {str(e)}"

@mcp.tool()
async def gemini_toggle_personal_intelligence(enabled: bool) -> str:
    """
    Toggles Personal Intelligence Labs features via the 'More tools > Personal Intelligence' path.
    """
    try:
        await bridge.click_nested_menu(url=URL, menu_trigger=ATTACH_SEL, path=["More tools", "Personal Intelligence"])
        return f"[Gemini Status]\nPersonal Intelligence Labs option toggled (state request: {enabled})."
    except Exception as e:
        return f"Error toggling Personal Intelligence Labs: {str(e)}"

@mcp.tool()
async def gemini_download_file(file_name_pattern: Optional[str] = None) -> str:
    """
    Triggers download of the latest generated file, table, or image in Gemini, moving it to the project downloads folder.
    """
    click_selector = "button[aria-label*='Download'], a[download], [class*='download'] button, button[aria-label*='Export']"
    try:
        await bridge.click_and_wait(url=URL, click_selector=click_selector, wait_ms=8000)
        status = bridge.move_latest_download(project_name="ai agents challenge", file_pattern=file_name_pattern)
        return f"[Gemini Download Status]\n{status}"
    except Exception as e:
        return f"Error exporting Gemini output: {str(e)}"

@mcp.tool()
async def gemini_download_multiple_files(file_name_patterns: List[str]) -> str:
    """
    Triggers download of multiple outputs and moves them to the project downloads folder.
    """
    click_selector = "button[aria-label*='Download'], a[download], [class*='download'] button"
    try:
        await bridge.click_and_wait(url=URL, click_selector=click_selector, wait_ms=5000)
        status = bridge.move_multiple_downloads(project_name="ai agents challenge", count=len(file_name_patterns))
        return f"[Gemini Download Status]\n{status}"
    except Exception as e:
        return f"Error executing multiple downloads: {str(e)}"

@mcp.tool()
async def gemini_custom_gem(gem_url: str, prompt: str) -> str:
    """
    Interacts with a specific custom Gem using its URL.
    :param gem_url: The full URL to the custom Gem.
    :param prompt: The query to send.
    """
    if not gem_url.startswith("https://gemini.google.com/"):
        return "Error: Invalid Gem URL. Must start with https://gemini.google.com/"
    try:
        content = await bridge.interact(
            url=gem_url, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt
        )
        return f"[Gem Response]\n{content}"
    except Exception as e:
        return f"Error executing custom Gem: {str(e)}"

@mcp.tool()
async def gemini_workspace_query(extension: str, prompt: str) -> str:
    """
    Queries Gemini with a Google Workspace extension activated.
    :param extension: The extension to target (e.g. Gmail, Drive, Docs, YouTube, Maps, Flights, Hotels).
    :param prompt: The actual search or query prompt.
    """
    formatted_prompt = f"@{extension.title()} {prompt}"
    try:
        content = await bridge.interact(
            url=URL, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=formatted_prompt
        )
        return f"[Gemini Workspace Response]\n{content}"
    except Exception as e:
        return f"Error executing Gemini Workspace query: {str(e)}"

@mcp.tool()
async def gemini_double_check() -> str:
    """
    Triggers Google Search verification (Double-check response) for the current Gemini page response.
    """
    click_selector = "button[aria-label*='Double-check response'], button[aria-label*='Verify'], [class*='double-check']"
    try:
        await bridge.click_and_wait(url=URL, click_selector=click_selector, wait_ms=4000)
        return "[Gemini Status]\nDouble-check triggered successfully. View your browser tab to see search verification status."
    except Exception as e:
        return f"Error triggering Gemini Double-check: {str(e)}"

@mcp.tool()
async def gemini_get_conversations() -> str:
    """
    Retrieves the list of recent conversations from the Gemini sidebar.
    """
    selector = "a[href*='/chat/'], a[href*='/app/chat/']"
    try:
        results = await bridge.scrape_links_and_text(url=URL, selector=selector)
        if not results:
            return "No recent Gemini conversations found or sidebar is hidden."
        output = ["--- Recent Gemini Conversations ---"]
        for res in results:
            text = res["text"].replace("\n", " ").strip()
            href = res["href"]
            if text and not text.startswith("New chat"):
                output.append(f"- {text} (URL: https://gemini.google.com{href})")
        return "\n".join(output)
    except Exception as e:
        return f"Error retrieving Gemini conversations: {str(e)}"

@mcp.tool()
async def gemini_new_conversation() -> str:
    """
    Navigates Gemini to a fresh new conversation (blank chat).
    """
    try:
        from common_browser import connect_to_chrome
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await connect_to_chrome(p)
            for context in browser.contexts:
                for page in context.pages:
                    if "gemini.google.com" in page.url:
                        await page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
                        return "Navigated to new Gemini conversation."
            return "No Gemini tab found. Open gemini.google.com first."
    except Exception as e:
        return f"Error starting new conversation: {str(e)}"

@mcp.tool()
async def gemini_open_conversation(conversation_url: str) -> str:
    """
    Opens a specific Gemini conversation by its URL and returns its content.
    :param conversation_url: Full Gemini conversation URL.
    """
    if not conversation_url.startswith("https://gemini.google.com/"):
        return "Error: URL must start with https://gemini.google.com/"
    try:
        content = await bridge.interact(url=conversation_url, wait_selector=WAIT_SEL)
        return f"[Gemini Conversation Content]\n{content}"
    except Exception as e:
        return f"Error opening conversation: {str(e)}"

if __name__ == "__main__":
    mcp.run()
