import os
import sys
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Page

async def connect_to_chrome(p, cdp_url: str = "http://127.0.0.1:9222"):
    # 1. Try to connect directly
    try:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        if browser.contexts:
            return browser
    except Exception:
        pass

    # 2. Try to auto-start user's Chrome with remote debugging
    try:
        import subprocess
        chrome_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Chromium\chrome-win\chrome.exe"),
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if chrome_path:
            debug_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".chrome-debug-profile"))
            os.startfile(
                chrome_path,
                arguments=f'--remote-debugging-port=9222 --user-data-dir="{debug_dir}"'
            )
            # Wait for Chrome to start up and bind to the port (up to 3 seconds)
            for _ in range(6):
                await asyncio.sleep(0.5)
                try:
                    browser = await p.chromium.connect_over_cdp(cdp_url)
                    if browser.contexts:
                        return browser
                except Exception:
                    continue
    except Exception:
        pass

    # 3. If both failed, raise RuntimeError with clear instructions
    raise RuntimeError(
        "Could not connect to Chrome remote debugging on port 9222.\n"
        "Please ensure that:\n"
        "1. All Chrome instances are closed.\n"
        "2. Chrome is launched using your desktop shortcut:\n"
        "   \"C:\\Users\\Admin\\OneDrive\\Desktop\\we.lnk\"\n"
        "   (which runs with --remote-debugging-port=9222)\n"
        "Or run the following command in PowerShell:\n"
        "   & \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --profile-directory=\"Profile 1\" --remote-debugging-port=9222"
    )

class BrowserBridge:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.cdp_url = "http://127.0.0.1:9222"

    async def get_page(self, p, target_url: str):
        browser = await connect_to_chrome(p, self.cdp_url)
        contexts = browser.contexts
        for context in contexts:
            for page in context.pages:
                if target_url in page.url:
                    return browser, page
        # If no matching page found, open a new page in the first context
        context = contexts[0]
        page = await context.new_page()
        await page.goto(target_url, wait_until="domcontentloaded")
        return browser, page

    async def interact(self, url: str, wait_selector: str, input_selector: Optional[str] = None, 
                       prompt: Optional[str] = None, upload_path: Optional[str] = None, 
                       click_selector: Optional[str] = None) -> str:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                # 1. Handle File Upload if provided
                if upload_path:
                    file_input = page.locator("input[type='file']")
                    if await file_input.count() > 0:
                        await file_input.set_input_files(upload_path)
                    else:
                        async with page.expect_file_chooser() as fc_info:
                            await page.click("button[aria-label*='upload'], button[aria-label*='file'], [class*='upload']")
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(upload_path)
                    await asyncio.sleep(2)

                # 2. Click specific features if requested
                if click_selector:
                    await page.wait_for_selector(click_selector, timeout=15000)
                    await page.click(click_selector)
                    await asyncio.sleep(1)

                # 3. Input prompt
                if input_selector and prompt:
                    await page.wait_for_selector(input_selector, timeout=15000)
                    await page.fill(input_selector, prompt)
                    await page.keyboard.press("Enter")
                
                # 4. Wait for response container
                await page.wait_for_selector(wait_selector, timeout=45000)
                await asyncio.sleep(6)
                
                content = await page.evaluate("() => document.body.innerText")
                return content or "No content found"
            finally:
                if not is_cdp:
                    await obj.close()

    async def click_and_wait(self, url: str, click_selector: str, wait_selector: Optional[str] = None, wait_ms: int = 2000) -> str:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                await page.wait_for_selector(click_selector, timeout=15000)
                await page.click(click_selector)
                await asyncio.sleep(wait_ms / 1000.0)
                if wait_selector:
                    await page.wait_for_selector(wait_selector, timeout=30000)
                return "Action executed successfully"
            finally:
                if not is_cdp:
                    await obj.close()

    async def scrape_links_and_text(self, url: str, selector: str) -> list:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                await page.wait_for_selector(selector, timeout=10000)
                elements = page.locator(selector)
                count = await elements.count()
                results = []
                for i in range(count):
                    loc = elements.nth(i)
                    text = await loc.inner_text()
                    href = await loc.get_attribute("href")
                    results.append({"text": text.strip() if text else "", "href": href or ""})
                return results
            finally:
                if not is_cdp:
                    await obj.close()

    async def scrape_elements(self, url: str, selector: str) -> list:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                await page.wait_for_selector(selector, timeout=10000)
                elements = page.locator(selector)
                count = await elements.count()
                results = []
                for i in range(count):
                    text = await elements.nth(i).inner_text()
                    if text:
                        results.append(text.strip())
                return results
            finally:
                if not is_cdp:
                    await obj.close()

    async def create_note_in_notebook(self, url: str, note_title: str, note_content: str) -> str:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                add_note_selectors = [
                    "button[aria-label*='Add note']",
                    "button[aria-label*='create note']",
                    "button:has-text('Add note')",
                    "button:has-text('Create note')",
                    "[class*='add-note']",
                    "[class*='create-note']"
                ]
                clicked = False
                for sel in add_note_selectors:
                    try:
                        if await page.locator(sel).count() > 0:
                            await page.click(sel)
                            clicked = True
                            break
                    except Exception:
                        continue
                if not clicked:
                    await page.click("button[aria-label*='Add'], button[aria-label*='add']")
                await asyncio.sleep(2)
                title_selectors = [
                    "input[placeholder*='Title']",
                    "input[placeholder*='title']",
                    "[placeholder*='Title']",
                    "textarea[placeholder*='Title']"
                ]
                for sel in title_selectors:
                    try:
                        if await page.locator(sel).count() > 0:
                            await page.fill(sel, note_title)
                            break
                    except Exception:
                        continue
                content_selectors = [
                    "textarea[placeholder*='Note']",
                    "textarea[placeholder*='content']",
                    "[contenteditable='true']",
                    "textarea"
                ]
                for sel in content_selectors:
                    try:
                        if await page.locator(sel).count() > 0:
                            await page.fill(sel, note_content)
                            break
                    except Exception:
                        continue
                save_selectors = [
                    "button:has-text('Save')",
                    "button:has-text('Done')",
                    "button[aria-label*='Save']",
                    "button[aria-label*='Close']"
                ]
                for sel in save_selectors:
                    try:
                        if await page.locator(sel).count() > 0:
                            await page.click(sel)
                            break
                    except Exception:
                        continue
                await asyncio.sleep(2)
                return "Note created successfully"
            except Exception as e:
                return f"Error creating note: {str(e)}"
            finally:
                if not is_cdp:
                    await obj.close()

    async def click_nested_menu(self, url: str, menu_trigger: str, path: list) -> str:
        async with async_playwright() as p:
            obj, page = await self.get_page(p, url)
            is_cdp = hasattr(obj, "contexts")
            try:
                await page.wait_for_selector(menu_trigger, timeout=10000)
                await page.click(menu_trigger)
                await asyncio.sleep(1)
                for item in path:
                    selector = f"text='{item}', :has-text('{item}'), [aria-label*='{item}']"
                    loc = page.locator(selector).first
                    await loc.wait_for(state="visible", timeout=8000)
                    await loc.click()
                    await asyncio.sleep(1)
                return "Menu path clicked successfully"
            except Exception as e:
                return f"Error clicking menu path {path}: {str(e)}"
            finally:
                if not is_cdp:
                    await obj.close()

    def move_latest_download(self, project_name: str, file_pattern: str = None) -> str:
        import shutil
        import glob
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        downloads_dir = os.path.join(user_profile, "Downloads")
        dest_dir = os.path.join("F:\\mcp-data", project_name)
        os.makedirs(dest_dir, exist_ok=True)
        files = glob.glob(os.path.join(downloads_dir, "*"))
        if not files:
            return "No files found in Downloads folder."
        files.sort(key=os.path.getmtime, reverse=True)
        matched_file = None
        if file_pattern:
            for f in files:
                if file_pattern.lower() in os.path.basename(f).lower():
                    matched_file = f
                    break
        else:
            matched_file = files[0]
        if not matched_file:
            return f"No files matching '{file_pattern}' found."
        ext = os.path.splitext(matched_file)[1]
        if ext in ['.crdownload', '.tmp', '.part']:
            return "Download is still in progress."
        filename = os.path.basename(matched_file)
        dest_path = os.path.join(dest_dir, filename)
        try:
            shutil.move(matched_file, dest_path)
            return f"Successfully downloaded and moved to: {dest_path}"
        except Exception as e:
            return f"Error moving file: {str(e)}"

    def move_multiple_downloads(self, project_name: str, count: int = 1) -> str:
        import shutil
        import glob
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        downloads_dir = os.path.join(user_profile, "Downloads")
        dest_dir = os.path.join("F:\\mcp-data", project_name)
        os.makedirs(dest_dir, exist_ok=True)
        files = glob.glob(os.path.join(downloads_dir, "*"))
        if not files:
            return "No files found in Downloads folder."
        files.sort(key=os.path.getmtime, reverse=True)
        moved_files = []
        for i in range(min(count, len(files))):
            f = files[i]
            ext = os.path.splitext(f)[1]
            if ext in ['.crdownload', '.tmp', '.part']:
                continue
            filename = os.path.basename(f)
            dest_path = os.path.join(dest_dir, filename)
            try:
                shutil.move(f, dest_path)
                moved_files.append(dest_path)
            except Exception:
                continue
        if moved_files:
            return f"Successfully downloaded and moved: {', '.join(moved_files)}"
        return "No files were moved."
