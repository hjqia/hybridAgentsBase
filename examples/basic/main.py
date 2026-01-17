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
    parser = argparse.ArgumentParser(description="Run the Hybrid Agent.")
    parser.add_argument("--topic", type=str, default="AI Agents", help="Topic to research.")
    parser.add_argument("--user-id", type=str, default="user-default", help="Helpful if tracing is used")
    parser.add_argument("--mcp-urls", nargs="+", help="MCP Server URLs.")
    args = parser.parse_args()

    session_id = f"session-{uuid.uuid4()}"
    user_id = args.user_id

    otel_env = os.getenv("ENABLE_OPEN_TELEMETRY", "false").lower()
    tracing_enabled = otel_env in ("true", "1", "t", "yes")

    # Setup Langfuse / OpenTelemetry for smolagents with session ID and User ID
    if tracing_enabled:
        setup_smolagents_instrumentation(session_id=session_id, user_id=user_id, tracing_enabled=tracing_enabled)
    else:
        print(f"--- Telemetry disabled [Session: {session_id}, User: {user_id}] ---")

    print(f"--- Starting Agent Session: {session_id} ---")

    # Shared State Initialization
    shared_state = {
        "input": {
            "topic": args.topic,
            "mcp_urls": args.mcp_urls or [],
            "session_id": session_id,
            "user_id": user_id
        }
    }

    # Run Flow
    flow = get_flow(session_id, user_id, tracing_enabled)
    flow.run(shared_state)

    # Output Results
    res = shared_state.get("research", {}).get("result")
    if res:
        print("\n--- Result ---")
        print(f"Summary: {res.summary}")
        print(f"Confidence: {res.confidence}")
    else:
        print("\n--- Failed ---")
        print("No result generated.")


if __name__ == "__main__":
    main()
