from pocketflow import Flow
from nodes import InputNode, PlanNode, ApprovalNode, ExecuteNode, SaveMemoryNode, EndNode
import os

class CLIAgentFlow(Flow):
    def __init__(self, start):
        super().__init__(start=start)

def get_flow(session_id, user_id, tracing_enabled):
    input_node = InputNode()
    plan_node = PlanNode()
    approve_node = ApprovalNode()
    exec_node = ExecuteNode()
    save_mem_node = SaveMemoryNode()
    end_node = EndNode()

    # Define Graph
    
    # 1. Start -> Input
    input_node - "continue" >> plan_node
    input_node - "exit" >> end_node
    
    # 2. Input -> Plan -> Approval
    plan_node - "success" >> approve_node
    plan_node - "error" >> input_node # Try again
    
    # 3. Approval -> Execute or Back
    approve_node - "approve" >> exec_node
    approve_node - "reject" >> input_node
    
    # 4. Execute -> Save Memory (if success) or Back
    exec_node - "success" >> save_mem_node
    exec_node - "failure" >> input_node
    
    # 5. Save -> Loop back to Input
    save_mem_node - "next" >> input_node

    return CLIAgentFlow(start=input_node)
