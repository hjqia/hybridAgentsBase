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
    parser = argparse.ArgumentParser(description="Human Input Example Agent")
    parser.add_argument("--question", type=str, default="What is your favorite color?", help="Question to ask the user.")
    parser.add_argument("--user-id", default="user-default")

    args = parser.parse_args()

    session_id = f"session-{uuid.uuid4()}"
    user_id = args.user_id

    otel_env = os.getenv("ENABLE_OPEN_TELEMETRY", "false").lower()
    tracing_enabled = otel_env in ("true", "1", "t", "yes")

    if tracing_enabled:
        setup_smolagents_instrumentation(session_id=session_id, user_id=user_id, tracing_enabled=tracing_enabled)

    print(f"--- Starting Session: {session_id} ---")

    shared_state = {
        "input": {
            "human_question": args.question,
            "session_id": session_id,
            "user_id": user_id
        }
    }

    flow = get_flow(session_id, user_id, tracing_enabled)
    flow.run(shared_state)

    result = shared_state.get("greeter", {}).get("response")
    human_in = shared_state.get("ask_human", {}).get("response")

    if result:
        print("\n--- Interaction Result ---")
        print(f"User Answered: {human_in}")
        print(f"Agent Replied: {result.greeting}")
    else:
        print("\n--- Failed ---")
        print("No response generated.")


if __name__ == "__main__":
    main()
