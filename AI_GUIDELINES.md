# AI Coding Guidelines for Hybrid Agent Framework

You are acting as a developer for a Hybrid Agent framework using **PocketFlow** (orchestration) and **smolagents** (execution).
Follow these strict architectural rules when adding features.

## 1. Core Philosophy
- **Orchestration vs Execution**: `flow.py` manages the path. `nodes.py` manages the work.
- **Strict Typing**: All agent outputs must be structured via **Pydantic** models in `models.py`.
- **Resilience**: Never run an agent raw. Always use `run_and_validate` to enable self-correction loops.

## 2. Implementation Steps (The Checklist)

When asked to "Add a new capability" or "Create a node":

### Step A: Model (`models.py`)
Define the output schema first.
```python
class MyNewResult(BaseModel):
    analysis: str
    score: int
```

### Step B: Prompt (`prompts.py`)
Create a function that returns the task string.
```python
def my_new_task(data: str) -> str:
    return f"Analyze {data}. Return JSON with 'analysis' and 'score'."
```

### Step C: Node (`nodes.py`)
1. Inherit from `BaseNode` (from `core.base_node`).
2. Implement `prep(self, shared)` to extract data from state.
3. Implement `exec(self, inputs)`:
   - Instantiate tools.
   - Call `self.run_and_validate(...)`.
   - **Crucial**: Pass `response_model=MyNewResult` and `result_key="my_key"`.
   - Return `"success"` or `"error"`.

### Step D: Flow (`flow.py`)
1. Import the new node.
2. Add it to `get_flow`.
3. Link it: `previous_node - "success" >> my_new_node`.

## 3. Critical Rules
- **Do NOT modify `core/`**: This directory contains the framework infrastructure.
- **Tools**: If a node needs a custom tool, add it to `tools.py` first.
- **State**: Read inputs from `shared['input']` or previous node namespaces. Write outputs automatically via `run_and_validate`.

## 4. Code Pattern Example
```python
# nodes.py
class ValidationNode(BaseNode):
    def prep(self, shared):
        return {"data": shared.get("research", {}).get("result"), "shared": shared}

    def exec(self, inputs):
        # ... setup tools ...
        status = self.run_and_validate(
            agent=agent,
            task=my_task(inputs["data"]),
            response_model=ValidationResult,
            shared=inputs["shared"],
            result_key="validated_data", # Will be accessible at shared['validation']['validated_data']
            system_prompt=SYSTEM_PROMPT
        )
        return status
```
