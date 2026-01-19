# Human-in-the-Loop Agent Example

This example demonstrates how to incorporate human interaction into an agent workflow using the `AskHumanNode`. The flow pauses execution, asks the user a question via the command line, captures the input, and then uses an LLM to generate a context-aware response.

## Features

*   **Human-in-the-Loop**: Seamlessly integrates user input into the automated workflow.
*   **Dynamic Prompting**: The question asked to the user can be configured via arguments or determined by previous nodes.
*   **State Persistence**: The user's input is stored in the shared state and accessible to subsequent nodes.

## Architecture

The workflow consists of:
1.  **`AskHumanNode`**: Pauses and prompts the user for input (blocking).
2.  **`GreeterNode`**: Reads the user's input and uses an LLM to generate a creative response.
3.  **`EndNode`**: Completes the flow.

## Usage

1.  **Run the agent:**
    ```bash
    python main.py --question "What is your favorite programming language?"
    ```

2.  **Interact:**
    The agent will pause and wait for your input:
    ```
    [AskHuman] What is your favorite programming language?
    (Type your answer and press Enter)
    > Python
    ```

3.  **Result:**
    The agent will process your input and respond:
    ```
    User Answered: Python
    Agent Replied: Python is a fantastic choice! Its readability and versatility make it a favorite for many developers. Happy coding!
    ```
