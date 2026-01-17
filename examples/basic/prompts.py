# --- Define your Prompts here ---

SYSTEM_PROMPT_EXAMPLE = (
    "You are a data extractor. You must extract the information into the correct JSON structure."
)

def example_task(topic: str) -> str:
    return (
        f"Research the topic: '{topic}'. "
        "Summarize the key points and provide a confidence score. "
        "Return the result as a strict JSON object with keys 'summary' and 'confidence'."
    )
