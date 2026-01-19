from pocketflow import Flow
from nodes import PriceNode, ConverterNode, RecommendationNode, EndNode
import os

class SymbolFlow(Flow):
    def __init__(self, start):
        super().__init__(start=start)

def get_flow(session_id, user_id, tracing_enabled=False):
    price = PriceNode()
    converter = ConverterNode()
    recommendation = RecommendationNode()
    end = EndNode()

    # Define Flow
    price - "success" >> converter
    price - "error" >> end
    
    converter - "success" >> recommendation
    converter - "error" >> end
    
    recommendation - "success" >> end
    recommendation - "error" >> end

    # Tracing
    if tracing_enabled and os.getenv("LANGFUSE_SECRET_KEY"):
        try:
            from core.tracing import trace_flow
            TracedFlow = trace_flow(
                flow_name="SymbolAnalysisFlow",
                session_id=session_id,
                user_id=user_id
            )(SymbolFlow)
            return TracedFlow(start=price)
        except ImportError:
            pass
            
    return SymbolFlow(start=price)
