# Basic Research Agent Example

This is a fundamental example of how to build an agent using the boilerplate. It demonstrates research-oriented task execution with local tools, web search capabilities, and optional MCP integration.

## Features

*   **Web Search**: Integrated `DuckDuckGoSearchTool` for real-time information gathering.
*   **Custom Tools**: Includes a `RandomNumberTool` to demonstrate how to build and register your own tools.
*   **MCP Support**: Can connect to any external MCP server to expand its capabilities.
*   **Structured Output**: Uses Pydantic models to ensure the research results follow a specific schema.
*   **Telemetry & Tracing**: Full support for OpenTelemetry and Langfuse to monitor agent performance and tool usage.

## Architecture

The example uses a simple two-node `pocketflow` graph:

1.  **`ResearchNode`**: The primary intelligence node. It initializes the `CodeAgent`, fetches tools, executes the research task, and validates the output against the `ExampleResult` model.
2.  **`EndNode`**: A simple terminal node that gracefully completes the flow.

## Setup

1.  **Configure Environment**:
    Make sure your `.env` file (at the project root or in this directory) has your LLM provider credentials (e.g., `OPENAI_API_KEY`).

2.  **Telemetry (Optional)**:
    If you want to use tracing, ensure `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set in your `.env`.

## Usage

### Basic Command
Run the agent on a specific topic:
```bash
python main.py --topic "The future of quantum computing"
```

### With Telemetry
Enable OpenTelemetry tracing by setting the environment variable:
```bash
ENABLE_OPEN_TELEMETRY=true python main.py --topic "Artificial General Intelligence" --user-id "researcher-1"
```

### With MCP Servers
Check the get_financial_symbols example 

## Result Format
The agent will output a structured result containing:
*   **Summary**: A concise summary of the research findings.
