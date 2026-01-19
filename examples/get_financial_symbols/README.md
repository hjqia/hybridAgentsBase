# Financial Symbol Analysis Agent

This example demonstrates a multi-step agent workflow using `smolagents` and the Model Context Protocol (MCP). The agent performs a financial analysis pipeline involving data fetching, transformation, and external service integration.

## Overview

The agent executes a linear flow consisting of three main stages:
1.  **Data Retrieval**: Fetches current stock/crypto prices in USD.
2.  **Data Transformation**: Converts the prices from USD to CAD.
3.  **External Analysis**: Queries an MCP (Model Context Protocol) server to generate trading recommendations and target prices.

## Architecture

The workflow is implemented using the `pocketflow` framework (part of the `core` library) with the following nodes:

*   **`PriceNode`**:
    *   **Input**: List of symbols (e.g., AAPL, BTC, ETH).
    *   **Action**: Uses a `PriceFetcherTool` to get raw price data.
    *   **Output**: JSON list of symbol data.

*   **`ConverterNode`**:
    *   **Input**: Price data from the previous step.
    *   **Action**: Uses a `CurrencyConverterTool` to apply an exchange rate (default 1.40 USD/CAD).
    *   **Output**: Augmented data with CAD prices.

*   **`RecommendationNode`**:
    *   **Input**: Converted price data.
    *   **Action**: Connects to an MCP Server (running locally or remotely) to use the `get_recommendation` tool.
    *   **Output**: Final analysis including Buy/Sell/Hold recommendations and target prices.

## Components

*   **`main.py`**: The entry point that initializes the agent flow and handles arguments.
*   **`nodes.py`**: Defines the three processing nodes (`PriceNode`, `ConverterNode`, `RecommendationNode`).
*   **`tools.py`**: Contains local tools (`PriceFetcherTool`, `CurrencyConverterTool`).
*   **`prompts.py`**: Stores the prompt templates for each step.
*   **`mock_price_api.py`**: A simple HTTP server mocking a financial data API.
*   **`mock_mcp_server.py`**: A FastMCP server providing the `get_recommendation` tool.

## Setup & Usage

### Prerequisites
Ensure you have the project dependencies installed in your virtual environment.

### Running the Example

The easiest way to run the full example (including the mock servers) is using the provided test script:

```bash
cd examples/get_financial_symbols
./test.sh
```

This script will:
1.  Start the `mock_price_api.py` (Price API) in the background.
2.  Start the `mock_mcp_server.py` (MCP Server) in the background.
3.  Run the `main.py` agent with sample symbols (AAPL, BTC, ETH).
4.  Clean up the background processes upon completion.

### Manual Run

If you want to run components separately:

1.  **Start the Price API:**
    ```bash
    python mock_price_api.py 8085
    ```

2.  **Start the MCP Server:**
    ```bash
    python mock_mcp_server.py
    ```
    (Runs on port 8080 by default)

3.  **Run the Agent:**
    ```bash
    python main.py --symbols AAPL BTC ETH --api-url http://localhost:8085 --mcp-url http://localhost:8080/sse
    ```

## Key Learnings

This example highlights:
*   **MCP Integration**: How to connect `smolagents` to an MCP server using `MCPClient`.
*   **Structured Output**: Ensuring robust communication between agents and tools by enforcing structured dictionary outputs.
*   **Prompt Hardening**: Techniques to ensure LLMs output valid code/JSON for parsing.