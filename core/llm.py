import os
import functools
import instructor
from litellm import completion
from smolagents.models import Model, MessageRole
from smolagents.agents import ChatMessage
from smolagents.monitoring import TokenUsage

# Constants
DEFAULT_PROVIDER = "openai"
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-sonnet-20240229",
    "ollama": "qwen2.5-coder:latest",
    "huggingface": "meta-llama/Meta-Llama-3-8B-Instruct"
}

class LiteLLMModel(Model):
    """Singleton wrapper for LiteLLM model configuration."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).lower()
        self.model_name = os.getenv("LLM_MODEL", DEFAULT_MODELS.get(self.provider, "gpt-4o"))
        self.api_base = os.getenv("LLM_PROVIDER_URL")
        self.api_key = self._get_api_key()
        
        # Format model ID for LiteLLM
        if self.provider == "ollama":
            self.model_id = f"ollama/{self.model_name}"
        elif self.provider == "huggingface":
            self.model_id = f"huggingface/{self.model_name}"
        elif self.provider == "anthropic":
            self.model_id = f"anthropic/{self.model_name}"
        else:
            self.model_id = self.model_name

    def _get_api_key(self):
        if self.provider == "openai": return os.getenv("OPENAI_API_KEY")
        if self.provider == "anthropic": return os.getenv("ANTHROPIC_API_KEY")
        if self.provider == "huggingface": return os.getenv("HF_TOKEN")
        return None

    def generate(self, messages, stop_sequences=None, **kwargs):
        # Convert smolagents messages to LiteLLM format
        formatted_messages = []
        for msg in messages:
            role = msg.role
            content = msg.content
            
            # Handle content being a list of dicts (e.g. from smolagents)
            if isinstance(content, list):
                # simplified: join text parts
                text_parts = [p.get('text', '') for p in content if p.get('type') == 'text']
                content = "\n".join(text_parts)

            if role == MessageRole.TOOL_CALL:
                formatted_role = "assistant"
            elif role == MessageRole.TOOL_RESPONSE:
                formatted_role = "user" # or "tool", but let's try user first for broader compatibility if tool_id is missing
            elif hasattr(role, "value"):
                formatted_role = role.value
            else:
                formatted_role = str(role)

            formatted_messages.append({"role": formatted_role, "content": content})

        response = completion(
            model=self.model_id,
            messages=formatted_messages,
            api_base=self.api_base,
            api_key=self.api_key,
            stop=stop_sequences,
            **kwargs
        )

        content = response.choices[0].message.content
        
        # Create TokenUsage
        usage = response.usage
        token_usage = TokenUsage(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens
        )

        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            token_usage=token_usage
        )

    def __call__(self, messages, stop_sequences=None, **kwargs):
        return completion(
            model=self.model_id,
            messages=messages,
            api_base=self.api_base,
            api_key=self.api_key,
            stop=stop_sequences,
            **kwargs
        )

@functools.lru_cache(maxsize=1)
def get_model_object():
    return LiteLLMModel()

@functools.lru_cache(maxsize=1)
def get_instructor_client():
    model = get_model_object()
    if model.provider == "openai":
        import openai
        return instructor.from_openai(openai.OpenAI(api_key=model.api_key))
    elif model.provider == "anthropic":
        import anthropic
        return instructor.from_anthropic(anthropic.Anthropic(api_key=model.api_key))
    else:
        # Fallback for generic/LiteLLM support
        import openai
        return instructor.from_openai(
            openai.OpenAI(base_url=model.api_base, api_key="placeholder"),
            mode=instructor.Mode.JSON
        )
