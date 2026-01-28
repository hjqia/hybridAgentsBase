import re
import json
import os
from pocketflow import Node
from .llm import get_model_object, get_instructor_client
from .smolagents_factory import run_agent_with_context
from .storage.fs import FileSystemStatePersistence
from .storage.base import FlowState


class PowerfulNode(Node):
    """
    PowerfulNode containing shared helpers for JSON parsing, LLM repair,
    namespaced state management, and automatic checkpointing.
    """

    @property
    def model(self):
        return get_model_object()

    @property
    def namespace(self) -> str:
        # Defaults to snake_case of class name (e.g. MyNode -> my)
        name = self.__class__.__name__
        if name.endswith('Node'):
            name = name[:-4]
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return name

    def _init_namespace(self, shared: dict):
        if self.namespace not in shared:
            shared[self.namespace] = {}

    def _write_namespace(self, shared: dict, **updates):
        self._init_namespace(shared)
        shared[self.namespace].update(updates)

    def _read_namespace(self, shared: dict, namespace: str = None) -> dict:
        return shared.get(namespace or self.namespace, {})

    def _log(self, message):
        if os.getenv("POCKETFLOW_LOG_LEVEL", "INFO").upper() != "OFF":
            print(message)

    def _clean_and_parse_json(self, content):
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            raise ValueError("Content is not dict or string")

        # Remove markdown
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```', '', content)

        # Find JSON object
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            return json.loads(content[start:end + 1])
        raise ValueError("No JSON found")

    def _llm_repair(self, content: str, response_model, system_prompt: str):
        self._log(f"[{self.namespace}] Validation failed. Attempting LLM repair...")
        client = get_instructor_client()
        model_id = self.model.model_id
        if not os.getenv("OPENAI_API_KEY") and not model_id.startswith("huggingface/"):
            model_id = f"huggingface/{model_id}"

        return client.chat.completions.create(
            model=model_id,
            response_model=response_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(content)}
            ]
        )

    def parse_and_validate(self, exec_res, response_model, system_prompt: str, result_key: str, shared: dict):
        # 1. Fast Path
        try:
            data = self._clean_and_parse_json(exec_res)
            validated = response_model(**data)
            self._write_namespace(shared, status="success", **{result_key: validated})
            shared[self.namespace][result_key] = validated  # Direct access
            return "success"
        except Exception:
            pass

        # 2. Repair Path
        try:
            validated = self._llm_repair(exec_res, response_model, system_prompt)
            self._write_namespace(shared, status="repaired", **{result_key: validated})
            shared[self.namespace][result_key] = validated
            return "success"
        except Exception as e:
            error_msg = str(e)
            self._write_namespace(shared, status="error", error=error_msg)
            # Global error log
            if "errors" not in shared:
                shared["errors"] = {}
            shared["errors"][self.namespace] = {"message": error_msg, "raw": str(exec_res)[:200]}
            return "error"

    def run_and_validate(self, agent, task, response_model, shared, result_key, system_prompt, session_id=None, user_id=None, max_retries=3):
        current_task = task
        for attempt in range(max_retries):
            self._log(f"[{self.namespace}] Attempt {attempt + 1}/{max_retries}")
            res = run_agent_with_context(agent, current_task, session_id, user_id)

            if self.parse_and_validate(res, response_model, system_prompt, result_key, shared) == "success":
                return "success"

            error = shared.get("errors", {}).get(self.namespace, {}).get("message", "Unknown")
            self._log(f"[{self.namespace}] Failed: {error}")
            current_task = f"{task}\n\nPREVIOUS ERROR: {error}\nFIX THE FORMAT."

        return "error"

    def post(self, shared, prep_res, exec_res):
        """Checkpointing hook."""
        try:
            state = FlowState(
                session_id=shared["input"].get("session_id", "unknown"),
                user_id=shared["input"].get("user_id"),
                status="running",
                data=shared
            )
            FileSystemStatePersistence().save_state(state)
            self._log(f"[{self.namespace}] Checkpoint saved.")
        except Exception as e:
            self._log(f"[{self.namespace}] Checkpoint failed: {e}")
        return exec_res


class PowerfulBatchNode(PowerfulNode):
    def _exec(self, items):
        return [super(PowerfulBatchNode, self)._exec(i) for i in (items or [])]


"""
# This is up to the user to always import it from here, or just add it to the list of nodes in nodes.py
class EndNode(Node):
    def exec(self, inputs):
        return "Flow_ended"
"""
