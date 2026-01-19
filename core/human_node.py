from core.base_node import BaseNode

class AskHumanNode(BaseNode):
    """
    A node that pauses execution to ask the human user a question via stdin.
    stores the result in the shared state.
    """
    
    def prep(self, shared):
        # Allow dynamic question from previous nodes (e.g. stored in 'input' or 'context')
        # or use a default one.
        # Check if there is an explicit 'question' in the 'ask_human' namespace (self) or 'input'.
        
        # Priority:
        # 1. shared['ask_human']['question'] (if set by previous node targeting this one)
        # 2. shared['input']['human_question']
        # 3. Default
        
        pre_set_question = shared.get(self.namespace, {}).get("question")
        input_question = shared.get("input", {}).get("human_question")
        
        question = pre_set_question or input_question or "Please provide input:"
        
        return {
            "question": question,
            "shared": shared
        }

    def exec(self, inputs):
        question = inputs["question"]
        print(f"\n[AskHuman] {question}")
        print("(Type your answer and press Enter)")
        try:
            user_input = input("> ")
        except EOFError:
            # Handle case where input stream is closed (e.g. non-interactive run)
            print("[AskHuman] No input provided (EOF). Using empty string.")
            user_input = ""
            
        self._write_namespace(inputs["shared"], response=user_input)
        return "success"

