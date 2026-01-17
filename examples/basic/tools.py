from smolagents import Tool
import random

# --- Define your Custom Tools here ---

class RandomNumberTool(Tool):
    name = "get_random_number"
    description = "Generates a random number between a given range."
    inputs = {
        "min_val": {"type": "integer", "description": "Minimum value"},
        "max_val": {"type": "integer", "description": "Maximum value"}
    }
    output_type = "string"

    def forward(self, min_val: int, max_val: int) -> str:
        return str(random.randint(min_val, max_val))
