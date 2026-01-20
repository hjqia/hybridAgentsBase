from pocketflow import Node
from core import PowerfulNode
from core.smolagents_factory import get_agent, get_mcp_tools
from smolagents import DuckDuckGoSearchTool
from tools import RandomNumberTool
from models import ExampleResult
from prompts import example_task, SYSTEM_PROMPT_EXAMPLE


class ResearchNode(PowerfulNode):
    def prep(self, shared):
        # Get data from input
        return {
            "topic": shared.get("input", {}).get("topic", "AI Agents"),
            "mcp_urls": shared.get("input", {}).get("mcp_urls", []),
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id"),
            "shared": shared
        }

    def exec(self, inputs):
        topic = inputs["topic"]
        mcp_urls = inputs["mcp_urls"]

        print(f"\n[ResearchNode] Researching: {topic}")

        # Tools
        tools = [DuckDuckGoSearchTool(), RandomNumberTool()]
        mcp_client = None

        if mcp_urls:
            mcp_client, mcp_tools = get_mcp_tools(mcp_urls)
            if mcp_tools:
                tools.extend(mcp_tools)

        try:
            agent = get_agent(self.model, tools=tools)
            task = example_task(topic)

            # Execute with Retry & Validation
            status = self.run_and_validate(
                agent=agent,
                task=task,
                response_model=ExampleResult,
                shared=inputs["shared"],
                result_key="result",
                system_prompt=SYSTEM_PROMPT_EXAMPLE,
                session_id=inputs["session_id"],
                user_id=inputs["user_id"]
            )
            return status
        finally:
            if mcp_client:
                mcp_client.disconnect()


# This node is not actually required but helps to end the flow more cleanly
class EndNode(Node):
    def exec(self, inputs):
        return "Flow_ended"
