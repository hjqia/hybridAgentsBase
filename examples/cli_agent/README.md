# CLI Assistant Agent

A Bash-like assistant that executes shell commands based on natural language requests. It features a continuous feedback loop and long-term memory to learn from your preferences.

## Features

1.  **Interactive Loop**: Continuously accepts commands until you type 'exit'.
2.  **Safety First**: Always asks for approval before executing any generated shell command.
3.  **Memory System**:
    *   If you approve a command and it runs successfully, the agent asks if you want to remember it.
    *   In future sessions, if you ask for the same thing (or something similar), it retrieves the saved command immediately without re-generating it via LLM.
4.  **Local Execution**: Runs commands directly on your host machine (use with caution!).

## Architecture

*   **`InputNode`**: Handles the main prompt loop.
*   **`PlanNode`**: Checks `FileSystemAgentMemory` for existing solutions. If none, uses `CodeAgent` to generate a bash command.
*   **`ApprovalNode`**: Gates execution requiring explicit 'y' from user.
*   **`ExecuteNode`**: Runs the command using `subprocess`.
*   **`SaveMemoryNode`**: Persists successful LLM-generated commands to `.memories/`.

## Usage

1.  **Run the Agent**:
    ```bash
    python main.py
    ```

2.  **Example Session**:
    ```text
    CLI AGENT: What would you like to do?
    > list files in current dir

    [Planner] Thinking of a command...
    [Confirm] I will run:
      ls -la
    Proceed? (y/n)
    > y

    [Exec] Running...
    ... output ...
    
    [Memory] Should I remember this command for next time? (y/n)
    > y
    [Memory] Saved.
    ```

3.  **Next Time**:
    ```text
    CLI AGENT: What would you like to do?
    > list files in current dir

    [Memory] Found similar past task: list files in current dir
    [Memory] Suggested Command: ls -la
    
    [Confirm] I will run:
      ls -la
    ```
