# Hybrid Agent Boilerplate

This is a robust, production-ready template for building AI Agents using **PocketFlow** (orchestration) and **smolagents** (execution).

## 🚀 Getting Started

### 1. Installation
Create a virtual env, for example uv
```bash
uv pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your API keys:
```ini
LLM_PROVIDER=openai  # or anthropic, ollama, huggingface
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o

# Telemetry / Tracing (Optional)
ENABLE_OPEN_TELEMETRY=true  (enables both, smolagents and pocketflow telemetry)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
POCKETFLOW_TRACING_DEBUG=false   (to enable debug of PocketFlow telemetry)
```

### 3. Run the Example
```bash
cd examples/basic
python main.py --topic "Future of AI"
```

## 🛠️ How to Build Your Agent

### Step 1: Define Data Models (`models.py`)
Define what you want your agent to produce using Pydantic.
```python
class MyResult(BaseModel):
    answer: str
    references: List[str]
```

### Step 2: Write Prompts (`prompts.py`)
Write the instructions for the LLM.
```python
def my_task(query):
    return f"Research '{query}' and return JSON with 'answer' and 'references'."
```

### Step 3: Create Tools (`tools.py`)
Add custom tools if needed (standard Python classes inheriting from `Tool`).

### Step 4: Create Nodes (`nodes.py`)
Create a new class inheriting from `BaseNode`.
1. Implement `prep(self, shared)`: Prepare inputs.
2. Implement `exec(self, inputs)`: Run the agent using `self.run_and_validate(...)`.

### Step 5: Define the Flow (`flow.py`)
Wire your nodes together.  Using PocketFlow special syntax
```python
node_a = MyNode()
node_b = AnotherNode()
node_c = ErrorNode()
node_a - "success" >> node_b
node_a - "error" >> node_c
```

## 📂 Structure
- `core/`: Framework logic (Do not edit unless necessary).
- `nodes.py`: Your workflow logic.
- `tools.py`: Your custom tools.
- `models.py`: Your data structures.
- `flow.py`: Your graph definition.
- `main.py`: Entry point.
