import subprocess
import uuid
from pocketflow import Node
from core import PowerfulNode
from core.smolagents_factory import get_agent
from core.storage.fs import FileSystemAgentMemory, AgentMemoryItem
from smolagents import Tool

# We'll use a simple tool to generate bash commands
class BashCommandGeneratorTool(Tool):
    name = "generate_bash"
    description = "Generates a bash command to fulfill a user request."
    inputs = {
        "request": {"type": "string", "description": "The user's natural language request"},
        "os_info": {"type": "string", "description": "Operating system information"}
    }
    output_type = "string"

    def forward(self, request: str, os_info: str) -> str:
        # This is a placeholder; the Agent's LLM will actually do the work
        # via the system prompt, but having a tool definition helps structure it
        # or we can just rely on the agent's conversation.
        # Actually, for this node, we might not even need a tool if we just ask the LLM.
        return ""

class InputNode(PowerfulNode):
    def prep(self, shared):
        return {"shared": shared}

    def exec(self, inputs):
        print("\n" + "="*40)
        print("CLI AGENT: What would you like to do?")
        print("(Type 'exit' to quit)")
        print("="*40)
        user_input = input("> ").strip()
        
        self._write_namespace(inputs["shared"], user_input=user_input)
        
        if user_input.lower() in ["exit", "quit"]:
            return "exit"
        return "continue"

class PlanNode(PowerfulNode):
    def prep(self, shared):
        user_input = shared.get("input", {}).get("user_input")
        user_id = shared.get("input", {}).get("user_id")
        return {
            "user_input": user_input,
            "user_id": user_id,
            "shared": shared
        }

    def exec(self, inputs):
        user_input = inputs["user_input"]
        user_id = inputs["user_id"]
        
        memory = FileSystemAgentMemory()
        
        # 1. Search Memory
        # We look for exact matches or high similarity. 
        # For this simple example, we search for the exact string or contained string.
        # Ideally, we'd use semantic search.
        memories = memory.search_memories(user_id, user_input)
        
        # Simple heuristic: if we find a memory where the content (the goal) is very close
        match = None
        for m in memories:
            # We stored memory content as "Goal: [goal] | Command: [cmd]"
            # Let's parse it or store it better. 
            # Let's assume we store the Goal in 'content' and Command in 'metadata'.
            if user_input.lower() in m.content.lower():
                match = m
                break
        
        if match:
            cmd = match.metadata.get("command")
            print(f"\n[Memory] Found similar past task: {match.content}")
            print(f"[Memory] Suggested Command: {cmd}")
            self._write_namespace(inputs["shared"], command=cmd, source="memory")
            return "success"

        # 2. Generate if not found
        print("\n[Planner] Thinking of a command...")
        agent = get_agent(self.model)
        
        # System info
        import platform
        sys_info = f"{platform.system()} {platform.release()}"
        
        task = f"User wants: '{user_input}'. OS: {sys_info}. Provide a SINGLE bash command to achieve this. Return JSON with 'command'. Wrap code in <code> tags."
        
        # We use a quick inline struct
        from pydantic import BaseModel
        class CommandResult(BaseModel):
            command: str
            
        status = self.run_and_validate(
            agent=agent,
            task=task,
            response_model=CommandResult,
            shared=inputs["shared"],
            result_key="generated_command",
            system_prompt="You are a CLI expert. Output valid bash commands.",
            session_id=inputs["shared"].get("input", {}).get("session_id"),
            user_id=user_id
        )
        
        if status == "success":
            # Normalize to the same key 'command'
            gen_cmd = inputs["shared"]["plan"]["generated_command"].command
            self._write_namespace(inputs["shared"], command=gen_cmd, source="llm")
            return "success"
            
        return "error"

class ApprovalNode(PowerfulNode):
    def prep(self, shared):
        cmd = shared.get("plan", {}).get("command")
        return {"command": cmd, "shared": shared}

    def exec(self, inputs):
        cmd = inputs["command"]
        if not cmd:
            print("[Approval] No command to approve.")
            return "reject"
            
        print(f"\n[Confirm] I will run:\n  {cmd}\n")
        print("Proceed? (y/n)")
        ans = input("> ").strip().lower()
        
        if ans == 'y':
            return "approve"
        return "reject"

class ExecuteNode(PowerfulNode):
    def prep(self, shared):
        return {
            "command": shared.get("plan", {}).get("command"),
            "shared": shared
        }

    def exec(self, inputs):
        cmd = inputs["command"]
        print(f"\n[Exec] Running...")
        try:
            # Running with shell=True is dangerous but that's the point of this agent
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print("--- Output ---")
            print(result.stdout)
            if result.stderr:
                print("--- Error ---")
                print(result.stderr)
            print("--------------")
            
            success = (result.returncode == 0)
            self._write_namespace(inputs["shared"], success=success, output=result.stdout)
            
            if success:
                return "success"
            return "failure"
        except Exception as e:
            print(f"[Exec] Failed: {e}")
            return "failure"

class SaveMemoryNode(PowerfulNode):
    def prep(self, shared):
        return {
            "source": shared.get("plan", {}).get("source"),
            "user_input": shared.get("input", {}).get("user_input"),
            "command": shared.get("plan", {}).get("command"),
            "user_id": shared.get("input", {}).get("user_id"),
            "shared": shared
        }

    def exec(self, inputs):
        source = inputs["source"]
        
        # Only ask to save if it came from LLM (new) and it was successful (implied by reaching here?)
        # Actually ExecuteNode returns "success" or "failure". Flow should route failure to skip memory.
        
        if source == "memory":
            print("[Memory] (Already remembered)")
            return "next"

        print("\n[Memory] Should I remember this command for next time? (y/n)")
        ans = input("> ").strip().lower()
        
        if ans == 'y':
            memory = FileSystemAgentMemory()
            item = AgentMemoryItem(
                memory_id=str(uuid.uuid4()),
                user_id=inputs["user_id"],
                content=inputs["user_input"], # We index by the user's intent
                metadata={"command": inputs["command"]}
            )
            memory.add_memory(item)
            print("[Memory] Saved.")
            
        return "next"

class EndNode(Node):
    def exec(self, inputs):
        print("Bye!")
        return "Flow_ended"
