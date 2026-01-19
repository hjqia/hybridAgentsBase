from pocketflow import Flow
from nodes import AskHumanNode, GreeterNode, EndNode
import os

class HumanInteractionFlow(Flow):
    def __init__(self, start):
        super().__init__(start=start)

def get_flow(session_id, user_id, tracing_enabled):
    ask_node = AskHumanNode()
    greeter_node = GreeterNode()
    end_node = EndNode()

    # Define graph
    ask_node - "success" >> greeter_node
    greeter_node - "success" >> end_node
    greeter_node - "error" >> end_node

    # Tracing setup (boilerplate)
    has_tracing_backend = os.getenv("LANGFUSE_SECRET_KEY") is not None
    if tracing_enabled and has_tracing_backend:
        try:
            from core.tracing import trace_flow
            TracedFlow = trace_flow(
                flow_name="HumanInteractionFlow",
                session_id=session_id,
                user_id=user_id
            )(HumanInteractionFlow)
            return TracedFlow(start=ask_node)
        except Exception as e:
            print(f"Tracing init failed: {e}")

    return HumanInteractionFlow(start=ask_node)
