from pocketflow import Node
from core import PowerfulNode
from core.smolagents_factory import get_agent
from smolagents import Tool
from pydantic import BaseModel, Field

# We import AskHumanNode to expose it in this module if needed, 
# or just use it in flow.py
from core.human_node import AskHumanNode

class GreetingResponse(BaseModel):
    greeting: str = Field(description="The generated greeting message")

class GreeterNode(PowerfulNode):
    def prep(self, shared):
        # Get the human input from the AskHumanNode's namespace
        # Assuming the AskHumanNode was named 'ask_human' (default)
        human_response = shared.get("ask_human", {}).get("response", "")
        
        return {
            "human_input": human_response,
            "shared": shared,
            "session_id": shared.get("input", {}).get("session_id"),
            "user_id": shared.get("input", {}).get("user_id")
        }

    def exec(self, inputs):
        human_input = inputs["human_input"]
        
        if not human_input:
            print("[GreeterNode] No human input found.")
            return "error"

        print(f"[GreeterNode] Received: {human_input}")
        
        # Simple agent to greet back
        agent = get_agent(self.model)
        
        task = f"The user said: '{human_input}'. Write a polite and creative response/greeting to them. Return JSON with 'greeting'."
        
        status = self.run_and_validate(
            agent=agent,
            task=task,
            response_model=GreetingResponse,
            shared=inputs["shared"],
            result_key="response",
            system_prompt="You are a polite assistant.",
            session_id=inputs["session_id"],
            user_id=inputs["user_id"]
        )
        return status

class EndNode(Node):
    def exec(self, inputs):
        return "Flow_ended"
