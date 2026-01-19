import sys
import argparse
import uuid
import os
from dotenv import load_dotenv

# Ensure we can import from package root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(root_path)

from core.smolagents_factory import setup_smolagents_instrumentation
from flow import get_flow

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="CLI Agent")
    parser.add_argument("--user-id", default="default_user", help="User ID for memory context")
    args = parser.parse_args()

    session_id = f"session-{uuid.uuid4()}"
    user_id = args.user_id

    otel_env = os.getenv("ENABLE_OPEN_TELEMETRY", "false").lower()
    tracing_enabled = otel_env in ("true", "1", "t", "yes")

    if tracing_enabled:
        setup_smolagents_instrumentation(session_id=session_id, user_id=user_id, tracing_enabled=tracing_enabled)

    print(f"--- CLI Agent Started (User: {user_id}) ---")

    shared_state = {
        "input": {
            "session_id": session_id,
            "user_id": user_id
        }
    }

    # The flow will loop internally until 'exit' is returned
    flow = get_flow(session_id, user_id, tracing_enabled)
    flow.run(shared_state)

if __name__ == "__main__":
    main()
