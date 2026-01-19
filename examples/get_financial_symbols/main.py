import argparse
import uuid
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Ensure we can import from package root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(root_path)
from core.smolagents_factory import setup_smolagents_instrumentation
from flow import get_flow


def main():
    parser = argparse.ArgumentParser(description="Symbol Analysis Agent")
    parser.add_argument("--symbols", nargs="+", required=True, help="List of stock/crypto symbols")
    parser.add_argument("--api-url", required=True, help="URL of the price API")
    parser.add_argument("--mcp-url", required=True, help="URL of the MCP server")
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
            "symbols": args.symbols,
            "api_url": args.api_url,
            "mcp_url": args.mcp_url,
            "session_id": session_id,
            "user_id": user_id
        }
    }

    flow = get_flow(session_id, user_id, tracing_enabled)
    flow.run(shared_state)

    result = shared_state.get("recommendation", {}).get("final_analysis")
    if result:
        print("\n--- Final Analysis ---")
        for item in result.analyses:
            print(f"Symbol: {item.symbol} ({item.name})")
            print(f"Price (CAD): ${item.price_cad:.2f}")
            print(f"Recommendation: {item.recommendation}")
            print(f"Target Price: ${item.target_price:.2f}")
            print("-" * 20)
    else:
        print("\n--- Failed ---")
        errors = shared_state.get("errors", {})
        if errors:
            print("Errors:", errors)


if __name__ == "__main__":
    main()
