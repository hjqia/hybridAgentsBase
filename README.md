# Hybrid Agent Boilerplate

This is a robust, production-ready template for building AI Agents using **PocketFlow** (orchestration) and **smolagents** (execution). It includes a specialized **Web Automation Framework** for building resilient web agents.

## 🚀 Getting Started

### 1. Installation
Create a virtual env and install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

### 2. Configuration
Create a `.env` file with your API keys:
```ini
LLM_PROVIDER=openai  # or anthropic, ollama, huggingface
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o

# Web Agent Settings
BROWSER_HEADLESS=true  # Set to false to watch the agent work

# Telemetry / Tracing (Optional)
ENABLE_OPEN_TELEMETRY=true
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 🌐 Web Automation Framework

The boilerplate includes a powerful base for web agents located in `core/`.

### Key Features
- **Browser Sharing**: Reuses a single Playwright instance across multiple flow nodes for maximum speed.
- **Hybrid Auth Support**: Seamlessly teleports sessions using Cookies, JWT (LocalStorage), or both.
- **Visual Storyboarding**: Automatically captures `_start`, `_action`, and `_end` screenshots for every node in `artifacts/screenshots/`.
- **Auto-Repair**: Built-in logic to catch LLM formatting errors and retry with corrective feedback.

### Running the Web Example
1. **Start the Mock Server**:
   ```bash
   # Modes: cookie, jwt, or hybrid
   python web_playwright/server.py --mode hybrid
   ```
2. **Run the Agent**:
   ```bash
   python web_playwright/main.py --auth-mode hybrid
   ```

---

## 🛠️ How to Build Your Agent

### Step 1: Define Data Models (`models.py`)
Define what you want your agent to produce using Pydantic.

### Step 2: Create Web Nodes (`nodes.py`)
Inherit from `BaseWebNode` to get automatic browser management and storyboarding.
```python
from core.web_node import BaseWebNode

class MyWebTask(BaseWebNode):
    response_model = MyResult
    
    def prep_task(self, inputs):
        return f"Go to {inputs['url']} and perform the task..."
```

### Step 3: Cleanup (`flow.py`)
Always end your web flows with `WebEndNode` to ensure the browser is closed properly.
```python
from core.web_node import WebEndNode
from pocketflow import Flow

login = LoginNode()
action = WebAutomationNode()
cleanup = WebEndNode()

login >> action >> cleanup
```

---

## 📂 Structure
- `core/`: 
    - `web_node.py`: Base classes for web automation.
    - `web_tools.py`: Playwright toolkit (Browse, Click, Fill, etc.).
    - `sync_powerful_nodes.py`: The "Brain" with auto-repair and checkpointing.
- `web_playwright/`: Example implementation of a login + registration flow.
- `artifacts/`: Automatically generated screenshots and logs.
