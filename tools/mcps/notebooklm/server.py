import asyncio
import os
import sys
from typing import Optional, List
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_browser import BrowserBridge

mcp = FastMCP("NotebookLM-Web")
bridge = BrowserBridge("notebooklm")

BASE_URL = "https://notebooklm.google.com/notebook"
INPUT_SEL = "textarea[placeholder*='Ask a question']"
WAIT_SEL = ".chat-response-class, div[role='log']"

def notebook_url(notebook_id: str) -> str:
    return f"{BASE_URL}/{notebook_id}"

@mcp.tool()
async def ask_notebooklm(notebook_id: str, prompt: str) -> str:
    """
    Sends a query to a specific NotebookLM notebook and returns the AI response.
    :param notebook_id: The unique ID from the notebook URL.
    :param prompt: The question or instruction to send.
    """
    url = notebook_url(notebook_id)
    try:
        content = await bridge.interact(url=url, wait_selector=WAIT_SEL, input_selector=INPUT_SEL, prompt=prompt)
        return f"[NotebookLM Response]\n{content}"
    except Exception as e:
        return f"Error executing NotebookLM query: {str(e)}"

@mcp.tool()
async def upload_source_to_notebooklm(notebook_id: str, file_path: str) -> str:
    """
    Uploads a source file (PDF, TXT, MD, DOCX, etc.) to a NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    :param file_path: Absolute local path to the file to upload.
    """
    if not os.path.exists(file_path):
        return f"Error: Local file not found: {file_path}"
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Add source'], [class*='add-source']"
    try:
        await bridge.interact(
            url=url, wait_selector=WAIT_SEL,
            click_selector=click_selector, upload_path=file_path
        )
        return f"[NotebookLM Upload Status]\nUploaded source successfully: {os.path.basename(file_path)}"
    except Exception as e:
        return f"Error uploading source to NotebookLM: {str(e)}"

@mcp.tool()
async def notebooklm_upload_source(notebook_id: str, file_paths: List[str]) -> str:
    """
    Uploads one or multiple source files (PDF, EPUB, TXT, MD, etc.) to a specific NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    :param file_paths: List of absolute local file paths.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Add source'], [class*='add-source']"
    for fp in file_paths:
        if not os.path.exists(fp):
            return f"Error: Local file not found: {fp}"
    try:
        content = await bridge.interact(
            url=url, wait_selector=WAIT_SEL, 
            click_selector=click_selector, upload_path=file_paths
        )
        filenames = ", ".join([os.path.basename(fp) for fp in file_paths])
        return f"[NotebookLM Upload Status]\nUploaded source(s) successfully: {filenames}"
    except Exception as e:
        return f"Error uploading source to NotebookLM: {str(e)}"

@mcp.tool()
async def create_notebooklm_audio_overview(notebook_id: str) -> str:
    """
    Triggers generation of the dual-speaker Audio Overview podcast in a NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Audio Overview'], button[aria-label*='Generate']"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=3000)
        return "[NotebookLM Status]\nAudio Overview generation started. Check your browser tab for progress."
    except Exception as e:
        return f"Error generating NotebookLM Audio Overview: {str(e)}"

@mcp.tool()
async def notebooklm_create_audio_overview(notebook_id: str, customize_prompt: Optional[str] = None) -> str:
    """
    Triggers the generation of the dual-speaker Audio Overview podcast in NotebookLM, with optional customization instructions.
    :param notebook_id: The unique ID from the notebook URL.
    :param customize_prompt: Optional instructions to customize the style/focus of the audio overview.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Audio Overview'], button[aria-label*='Generate']"
    try:
        if customize_prompt:
            custom_selector = "textarea[placeholder*='Customize'], textarea[placeholder*='focus']"
            await bridge.interact(url=url, wait_selector=WAIT_SEL, input_selector=custom_selector, prompt=customize_prompt)
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nAudio Overview generation started."
    except Exception as e:
        return f"Error generating NotebookLM audio overview: {str(e)}"

@mcp.tool()
async def trigger_notebooklm_study_guide(notebook_id: str) -> str:
    """
    Generates a Study Guide document inside the NotebookLM notebook workspace.
    :param notebook_id: The unique ID from the notebook URL.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Study Guide'], button[aria-label*='guide']"
    try:
        content = await bridge.interact(url=url, wait_selector=WAIT_SEL, click_selector=click_selector)
        return f"[NotebookLM Study Guide]\n{content}"
    except Exception as e:
        return f"Error triggering NotebookLM Study Guide: {str(e)}"

@mcp.tool()
async def notebooklm_generate_study_guide(notebook_id: str) -> str:
    """
    Generates a Study Guide outline document inside the notebook workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Study Guide'], button[aria-label*='guide']"
    try:
        content = await bridge.interact(
            url=url, wait_selector=WAIT_SEL, click_selector=click_selector
        )
        return f"[NotebookLM Study Guide Summary]\n{content}"
    except Exception as e:
        return f"Error triggering NotebookLM study guide: {str(e)}"

@mcp.tool()
async def notebooklm_generate_faq(notebook_id: str) -> str:
    """
    Generates a FAQ guide outline in the NotebookLM workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='FAQ'], button:has-text('FAQ')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nFAQ generation triggered. View the document in your NotebookLM workspace."
    except Exception as e:
        return f"Error triggering FAQ generation: {str(e)}"

@mcp.tool()
async def notebooklm_generate_briefing_doc(notebook_id: str) -> str:
    """
    Generates a Briefing Document in the NotebookLM workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Briefing Document'], button[aria-label*='Briefing Doc'], button:has-text('Briefing Document')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nBriefing Document generation triggered. View the document in your NotebookLM workspace."
    except Exception as e:
        return f"Error triggering Briefing Document generation: {str(e)}"

@mcp.tool()
async def notebooklm_generate_timeline(notebook_id: str) -> str:
    """
    Generates a Timeline document outline in the NotebookLM workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Timeline'], button:has-text('Timeline')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nTimeline generation triggered. View the document in your NotebookLM workspace."
    except Exception as e:
        return f"Error triggering Timeline generation: {str(e)}"

@mcp.tool()
async def notebooklm_generate_table_of_contents(notebook_id: str) -> str:
    """
    Generates a Table of Contents document outline in the NotebookLM workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Table of Contents'], button:has-text('Table of Contents')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nTable of Contents generation triggered. View the document in your NotebookLM workspace."
    except Exception as e:
        return f"Error triggering Table of Contents generation: {str(e)}"

@mcp.tool()
async def notebooklm_create_video_overview(notebook_id: str) -> str:
    """
    Generates a Cinematic Video Overview outline in the NotebookLM workspace.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Video Overview'], button:has-text('Video Overview'), button:has-text('Cinematic Video')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nVideo Overview generation triggered. View the video output in your workspace."
    except Exception as e:
        return f"Error triggering Video Overview: {str(e)}"

@mcp.tool()
async def notebooklm_generate_slide_deck(notebook_id: str) -> str:
    """
    Generates and exports presentation slide decks in NotebookLM.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Slide Deck'], button[aria-label*='Slides'], button:has-text('Slides')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=4000)
        return "[NotebookLM Status]\nSlide Deck generation triggered."
    except Exception as e:
        return f"Error generating presentation slides: {str(e)}"

@mcp.tool()
async def notebooklm_generate_infographic(notebook_id: str, style: str) -> str:
    """
    Generates summaries formatted as custom visual Infographics.
    :param style: Infographic style (e.g. Kawaii, Professional, Bento Grid, Sketch Note).
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Infographic'], button:has-text('Infographic')"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=2000)
        style_selector = f"text='{style}', :has-text('{style}')"
        await bridge.click_and_wait(url=url, click_selector=style_selector, wait_ms=4000)
        return f"[NotebookLM Status]\nInfographic generation triggered in '{style}' style."
    except Exception as e:
        return f"Error generating Infographic: {str(e)}"

@mcp.tool()
async def notebooklm_create_note(notebook_id: str, note_title: str, note_content: str) -> str:
    """
    Creates a new note inside a NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    :param note_title: The title for the new note.
    :param note_content: The text body of the note.
    """
    url = notebook_url(notebook_id)
    try:
        status = await bridge.create_note_in_notebook(url=url, note_title=note_title, note_content=note_content)
        return f"[NotebookLM Status]\n{status}"
    except Exception as e:
        return f"Error creating note in NotebookLM: {str(e)}"

@mcp.tool()
async def notebooklm_list_sources(notebook_id: str) -> str:
    """
    Lists the titles of all active sources currently loaded in a NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    """
    url = notebook_url(notebook_id)
    selectors = [
        "div.source-title",
        "[class*='source-name']",
        "[class*='source-card']",
        "[class*='source-item']",
        "button[aria-label*='Source']",
    ]
    for sel in selectors:
        try:
            results = await bridge.scrape_elements(url=url, selector=sel)
            if results:
                unique_sources = sorted(set(r for r in results if r.strip()))
                output = [f"--- Sources in Notebook {notebook_id} ---"]
                for src in unique_sources:
                    output.append(f"- {src}")
                return "\n".join(output)
        except Exception:
            continue
    return "Error: Could not retrieve source list or no sources have been uploaded yet."

@mcp.tool()
async def notebooklm_get_chat_history(notebook_id: str) -> str:
    """
    Scrapes and returns the visible chat history from a NotebookLM notebook.
    :param notebook_id: The unique ID from the notebook URL.
    """
    url = notebook_url(notebook_id)
    selectors = [
        "div[role='log']",
        ".chat-message",
        "[class*='chat-content']",
        "[class*='message-content']",
    ]
    for sel in selectors:
        try:
            results = await bridge.scrape_elements(url=url, selector=sel)
            if results:
                output = [f"--- Chat History for Notebook {notebook_id} ---"]
                for msg in results:
                    output.append(msg)
                return "\n".join(output)
        except Exception:
            continue
    return "Could not retrieve chat history. The notebook may have no conversation yet."

@mcp.tool()
async def notebooklm_download_file(notebook_id: str, file_name_pattern: Optional[str] = None) -> str:
    """
    Triggers download of the latest generated document, guide, or slides in NotebookLM, relocating it to the project downloads folder.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Download'], button[aria-label*='Export'], a[download], [class*='download'] button"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=8000)
        status = bridge.move_latest_download(project_name="ai agents challenge", file_pattern=file_name_pattern)
        return f"[NotebookLM Download Status]\n{status}"
    except Exception as e:
        return f"Error exporting NotebookLM output: {str(e)}"

@mcp.tool()
async def notebooklm_download_multiple_files(notebook_id: str, file_name_patterns: List[str]) -> str:
    """
    Triggers download of multiple outputs in NotebookLM, relocating them to the project downloads folder.
    """
    url = notebook_url(notebook_id)
    click_selector = "button[aria-label*='Download'], button[aria-label*='Export'], a[download], [class*='download'] button"
    try:
        await bridge.click_and_wait(url=url, click_selector=click_selector, wait_ms=5000)
        status = bridge.move_multiple_downloads(project_name="ai agents challenge", count=len(file_name_patterns))
        return f"[NotebookLM Download Status]\n{status}"
    except Exception as e:
        return f"Error executing multiple downloads: {str(e)}"

if __name__ == "__main__":
    mcp.run()
