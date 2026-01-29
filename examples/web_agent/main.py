import sys
import argparse
import uuid
import os
import threading
import time
from dotenv import load_dotenv

# Ensure we can import from package root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from core.smolagents_factory import setup_smolagents_instrumentation
from flow import get_flow

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Run the Web Playwright Agent.")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000", help="URL of the form.")
    parser.add_argument("--name", type=str, default="John Doe", help="Name to fill.")
    parser.add_argument("--phone", type=str, default="123-456-7890", help="Phone to fill.")
    parser.add_argument("--email", type=str, default="john@example.com", help="Email to fill.")
    parser.add_argument("--user-id", type=str, default="user-web-demo", help="User ID for tracing.")
    parser.add_argument("--auth-mode", choices=["cookie", "jwt", "hybrid"], default="cookie", help="Authentication mode.")
    args = parser.parse_args()

    session_id = f"session-{uuid.uuid4()}"
    user_id = args.user_id
    
    # Store auth mode in env
    os.environ["AUTH_MODE"] = args.auth_mode

    otel_env = os.getenv("ENABLE_OPEN_TELEMETRY", "false").lower()
    tracing_enabled = otel_env in ("true", "1", "t", "yes")

    if tracing_enabled:
        setup_smolagents_instrumentation(session_id=session_id, user_id=user_id, tracing_enabled=tracing_enabled)
    else:
        print(f"--- Telemetry disabled [Session: {session_id}, User: {user_id}] ---")

    print(f"--- Starting Web Agent Session: {session_id} ---")

    # Shared State Initialization
    base_url = args.url.rstrip("/")
    if "?" not in base_url:
        target_url = f"{base_url}/?mode={args.auth_mode}"
    else:
        target_url = base_url

    shared_state = {
        "input": {
            "url": target_url,  # Now includes the mode!
            "name": args.name,
            "phone": args.phone,
            "email": args.email,
            "session_id": session_id,
            "user_id": user_id,
            "auth_mode": args.auth_mode
        }
    }

    # Run Flow
    flow = get_flow(session_id, user_id, tracing_enabled)
    flow.run(shared_state)

    # Output Results
    res_namespace = shared_state.get("web_automation", {})
    res = res_namespace.get("web_result")
    if res:
        print("\n--- Result ---")
        print(f"Success: {res.success}")
        print(f"Message: {res.message}")
        print(f"Data Submitted: {res.data_submitted}")
    else:
        print("\n--- Flow completed ---")
        print(f"Final shared state keys: {list(shared_state.keys())}")
        if "web_automation" in shared_state:
            print(f"web_automation keys: {list(shared_state['web_automation'].keys())}")

if __name__ == "__main__":
    main()
