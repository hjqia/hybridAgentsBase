import os
from pocketflow import Flow
from nodes import ResearchNode, EndNode


class AgentFlow(Flow):
    def __init__(self, start):
        super().__init__(start=start)


def get_flow(session_id, user_id, tracing_enabled):
    # 1. Instantiate Nodes
    research = ResearchNode()
    end = EndNode()

    # 2. Define Graph (PocketFlow syntax)
    research - "success" >> end
    research - "error" >> end

    # Ensure tracing backend (Langfuse) is also configured
    has_tracing_backend = os.getenv("LANGFUSE_SECRET_KEY") is not None

    if tracing_enabled and has_tracing_backend:
        try:
            from core.tracing import trace_flow

            # Create a traced version of the flow class
            TracedAgentFlow = trace_flow(
                flow_name="ResearchFlow",
                session_id=session_id,
                user_id=user_id
            )(AgentFlow)

            return TracedAgentFlow(start=research)
        except (ImportError, Exception) as e:
            print(f"[Flow] Tracing could not be initialized: {e}")

    return AgentFlow(start=research)
