from core import PowerfulNode
from core.smolagents_factory import get_agent
from core.web_tools import BrowseToPageTool, FillFormFieldTool, ClickButtonTool, PlaywrightThread, GetPageInfoTool
from pocketflow import Node

# Internal cache to avoid PocketFlow serialization errors
_WEB_THREAD_CACHE = {}

class BaseWebNode(PowerfulNode):
    """
    Handles the boilerplate of running a Playwright agent.
    - Manages browser sessions in a non-persistent cache to avoid serialization errors.
    """
    response_model = None
    system_prompt = """You are a professional web automation assistant.
CRITICAL RULES:
1. CODE FORMAT: You MUST wrap all Python code inside <code> blocks.
2. TOOL USAGE: Never assign the result of a tool to a variable with the same name as the tool. 
   - BAD: get_page_info = get_page_info()
   - GOOD: page_data = get_page_info()
3. BOOLEANS: Always use Python Booleans (True/False) in your final_answer.
4. FINAL ANSWER: You must always conclude your task by calling final_answer() with the requested JSON result."""
    result_key = "result"
    capture_screenshots = True  # Can be overridden in subclass or shared state

    def exec(self, inputs):
        shared = inputs.get("shared", {})
        session_id = inputs.get("session_id", "default")
        
        # Determine if screenshots should be captured (shared state override)
        should_capture = shared.get("capture_screenshots", self.capture_screenshots)
        
        # 1. Start or Reuse Playwright Thread from internal cache
        pw_thread = _WEB_THREAD_CACHE.get(session_id)
        
        if not pw_thread:
            storage_state = shared.get("storage_state")
            pw_thread = PlaywrightThread(storage_state=storage_state)
            pw_thread.start()
            pw_thread.ready.wait()
            _WEB_THREAD_CACHE[session_id] = pw_thread

        # 1. Pre-navigate for first-timers to avoid blank "start" screenshots
        if pw_thread.page.url == "about:blank" and inputs.get("url"):
            async def _go():
                await pw_thread.page.goto(inputs.get("url"))
            pw_thread.run_coro(_go())

        # 2. Initial Screenshot (Page as loaded)
        if should_capture:
            try:
                start_path = f"artifacts/screenshots/{session_id}/{self.__class__.__name__}_start.png"
                pw_thread.screenshot(start_path)
                print(f"[{self.__class__.__name__}] Initial screenshot saved to {start_path}")
            except Exception as e:
                print(f"[{self.__class__.__name__}] Failed to take initial screenshot: {e}")

        try:
            # 3. Setup Tools (Inject "action" screenshot into Click tool)
            action_path = None
            if should_capture:
                action_path = f"artifacts/screenshots/{session_id}/{self.__class__.__name__}_action.png"

            tools = [
                BrowseToPageTool(pw_thread), 
                FillFormFieldTool(pw_thread), 
                ClickButtonTool(pw_thread, screenshot_path=action_path), 
                GetPageInfoTool(pw_thread)
            ]
            agent = get_agent(self.model, tools=tools)
            
            # 4. Generate Task Instruction with Mission Constraints
            task = f"{self.prep_task(inputs)}\n\nMISSION CONSTRAINTS:\n{self.system_prompt}"

            # 5. Run and Validate
            status = self.run_and_validate(
                agent=agent,
                task=task,
                response_model=self.response_model,
                shared=shared,
                result_key=self.result_key,
                system_prompt=self.system_prompt,
                session_id=session_id,
                user_id=inputs.get("user_id")
            )

            # 6. Final Screenshot (Result)
            if should_capture:
                try:
                    end_path = f"artifacts/screenshots/{session_id}/{self.__class__.__name__}_end.png"
                    pw_thread.screenshot(end_path)
                    print(f"[{self.__class__.__name__}] Final screenshot saved to {end_path}")
                except:
                    pass

            # 7. Capture Session State
            shared["storage_state"] = pw_thread.get_storage_state()
            
            return status
        finally:
            pass

    def prep_task(self, inputs):
        raise NotImplementedError("Subclasses must implement prep_task")

class WebEndNode(Node):
    """A standard node to cleanup web resources at the end of a flow."""
    def prep(self, shared):
        return {
            "session_id": shared.get("input", {}).get("session_id", "default"),
            "shared": shared
        }

    def exec(self, inputs):
        session_id = inputs.get("session_id")
        pw_thread = _WEB_THREAD_CACHE.get(session_id)
        if pw_thread:
            print(f"[WebEndNode] Closing shared browser session: {session_id}")
            pw_thread.stop()
            del _WEB_THREAD_CACHE[session_id]
        return "Flow_ended"
