import os
from pocketflow import Flow
from nodes import LoginNode, WebAutomationNode, EndNode

class WebFlow(Flow):
    def __init__(self, start):
        super().__init__(start=start)

def get_flow(session_id, user_id, tracing_enabled):
    # 1. Instantiate Nodes
    login = LoginNode()
    automation = WebAutomationNode()
    end = EndNode()

    # 2. Define Graph: Login -> Automation -> End
    login - "success" >> automation
    login - "error" >> end
    
    automation - "success" >> end
    automation - "error" >> end

    # Tracing logic
    has_tracing_backend = os.getenv("LANGFUSE_SECRET_KEY") is not None

    if tracing_enabled and has_tracing_backend:
        try:
            from core.tracing import trace_flow
            TracedWebFlow = trace_flow(
                flow_name="WebAutomationFlow",
                session_id=session_id,
                user_id=user_id
            )(WebFlow)
            return TracedWebFlow(start=login)
        except (ImportError, Exception) as e:
            print(f"[Flow] Tracing could not be initialized: {e}")

    return WebFlow(start=login)
