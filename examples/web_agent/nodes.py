from core import BaseWebNode, WebEndNode
from pocketflow import Node
from models import WebFormResult
from login_models import LoginResult

# --- Specific Implementations ---

class LoginNode(BaseWebNode):
    response_model = LoginResult
    result_key = "login_result"
    system_prompt = """You are a login expert. Use get_page_info to find username/password fields, fill them, and click login. 
CRITICAL: return a JSON matching the LoginResult schema EXACTLY:
{
  "success": true,
  "message": "Login successful"
}
"""

    def prep(self, shared):
        base_url = shared.get("input", {}).get("url", "http://127.0.0.1:8000").split("?")[0].rstrip("/")
        auth_mode = shared.get("input", {}).get("auth_mode", "cookie")
        return {
            "url": f"{base_url}/login?mode={auth_mode}",
            "username": "admin",
            "password": "admin",
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id"),
            "shared": shared
        }

    def prep_task(self, inputs):
        return f"""Go to {inputs['url']} and login with username '{inputs['username']}' and password '{inputs['password']}'.
Confirm you are logged in and return the JSON answer with the 'success' key set to the Python Boolean True."""


class WebAutomationNode(BaseWebNode):
    response_model = WebFormResult
    result_key = "web_result"
    system_prompt = """You are an expert web automation agent. 
CRITICAL: return a JSON matching the WebFormResult schema EXACTLY using final_answer():
{
  "success": true,
  "message": "Form submitted successfully",
  "data_submitted": {
    "name": "...",
    "phone": "...",
    "email": "..."
  }
}
"""

    def prep(self, shared):
        i = shared.get("input", {})
        return {
            "url": i.get("url"),
            "name": i.get("name"),
            "phone": i.get("phone"),
            "email": i.get("email"),
            "session_id": i.get("session_id"),
            "user_id": i.get("user_id"),
            "shared": shared
        }

    def prep_task(self, inputs):
        return f"""COMPLETE REGISTRATION ON {inputs['url']}:
1. Use get_page_info() to confirm you are on the registration form.
2. Fill: Name="{inputs['name']}", Phone="{inputs['phone']}", Email="{inputs['email']}".
3. Submit the form.
4. return a JSON matching this schema EXACTLY:
{{
  "success": true,
  "message": "Form submitted successfully",
  "data_submitted": {{
    "name": "{inputs['name']}",
    "phone": "{inputs['phone']}",
    "email": "{inputs['email']}"
  }}
}}"""


class EndNode(WebEndNode):
    """Specific end node for this flow, inherits browser cleanup from core."""
    pass
