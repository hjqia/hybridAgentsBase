import asyncio
import threading
import time
import os
from smolagents import Tool
from playwright.async_api import async_playwright

class PlaywrightThread(threading.Thread):
    """A dedicated thread to run Playwright in its own event loop."""
    def __init__(self, storage_state: dict = None):
        super().__init__(daemon=True)
        self.loop = None
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.storage_state = storage_state
        self.ready = threading.Event()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._setup())
        self.ready.set()
        self.loop.run_forever()

    async def _setup(self):
        self.playwright = await async_playwright().start()
        
        # Check environment variable for headless mode, default to False so user can see it
        headless_env = os.getenv("BROWSER_HEADLESS", "false").lower()
        headless = headless_env in ("true", "1", "yes")
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=500 # Slow down actions by 500ms so they are visible
        )
        self.context = await self.browser.new_context(storage_state=self.storage_state)
        self.page = await self.context.new_page()

    async def _shutdown(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.loop.stop()

    def stop(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)

    def run_coro(self, coro):
        """Runs a coroutine in the playwright thread and waits for the result."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    def get_storage_state(self):
        async def _get():
            return await self.context.storage_state()
        return self.run_coro(_get())

class BrowseToPageTool(Tool):
    name = "browse_to_page"
    description = "Navigates the browser to a specific URL and returns the page content summary."
    inputs = {
        "url": {"type": "string", "description": "The URL to navigate to"}
    }
    output_type = "string"

    def __init__(self, pw_thread):
        super().__init__()
        self.pw_thread = pw_thread

    def forward(self, url: str) -> str:
        async def _logic():
            await self.pw_thread.page.goto(url)
            try:
                await self.pw_thread.page.wait_for_selector("form", timeout=5000)
            except:
                pass
            cur_url = self.pw_thread.page.url
            return f"Browsed to {url}. Current URL is {cur_url}."
        return self.pw_thread.run_coro(_logic())

class FillFormFieldTool(Tool):
    name = "fill_form_field"
    description = "Fills a form field with a value."
    inputs = {
        "selector": {"type": "string", "description": "The CSS selector of the input field (e.g., '#name')"},
        "value": {"type": "string", "description": "The value to enter"}
    }
    output_type = "string"

    def __init__(self, pw_thread):
        super().__init__()
        self.pw_thread = pw_thread

    def forward(self, selector: str, value: str) -> str:
        async def _logic():
            try:
                await self.pw_thread.page.wait_for_selector(selector, timeout=5000)
                await self.pw_thread.page.fill(selector, value)
                return f"Filled {selector} with '{value}'"
            except Exception as e:
                return f"Error: Could not fill '{selector}'. {str(e)}"
        return self.pw_thread.run_coro(_logic())

class ClickButtonTool(Tool):
    name = "click_button"
    description = "Clicks a button on the page."
    inputs = {
        "selector": {"type": "string", "description": "The CSS selector of the button (e.g., '#submitBtn')"}
    }
    output_type = "string"

    def __init__(self, pw_thread):
        super().__init__()
        self.pw_thread = pw_thread

    def forward(self, selector: str) -> str:
        async def _logic():
            # Wait for the selector to be attached to ensure it exists before clicking
            try:
                await self.pw_thread.page.wait_for_selector(selector, timeout=5000)
                await self.pw_thread.page.click(selector)
            except Exception as e:
                return f"Error: Could not find or click selector '{selector}'. Make sure you are using the correct ID from get_page_info."
            
            # Wait a bit for potential JS updates / animations
            await asyncio.sleep(1)
            
            # General feedback: What is the URL now? What changed?
            cur_url = self.pw_thread.page.url
            
            # Try to find a message but don't fail if #responseMessage isn't there
            msg = ""
            try:
                msg = await self.pw_thread.page.inner_text("#responseMessage")
            except:
                pass
                
            return f"Clicked {selector}. Current URL: {cur_url}. Observed message: {msg}"
        return self.pw_thread.run_coro(_logic())

class GetPageInfoTool(Tool):
    name = "get_page_info"
    description = "Returns a list of interactive elements (inputs, buttons, titles) on the current page to help identify selectors."
    inputs = {}
    output_type = "string"

    def __init__(self, pw_thread):
        super().__init__()
        self.pw_thread = pw_thread

    def forward(self) -> str:
        async def _logic():
            elements = await self.pw_thread.page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('input, button, h1, h2').forEach(el => {
                    results.push({
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        name: el.name,
                        placeholder: el.placeholder,
                        text: el.innerText || el.value,
                        type: el.type
                    });
                });
                return results;
            }""")
            
            summary = "Current URL: " + self.pw_thread.page.url + "\\nInteractive elements:\\n"
            for el in elements:
                summary += f"- {el['tag']}: ID='{el['id']}', Name='{el['name']}', Placeholder='{el['placeholder']}', Text='{el['text']}'\\n"
            
            return summary
        return self.pw_thread.run_coro(_logic())
