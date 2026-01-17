import os
import json
from typing import Optional
from .base import BaseStatePersistence, BaseAgentMemory, FlowState, AgentMemoryItem

class FileSystemStatePersistence(BaseStatePersistence):
    def __init__(self, base_dir: str = ".states"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.base_dir, f"{session_id}.json")

    def save_state(self, state: FlowState) -> bool:
        try:
            with open(self._get_path(state.session_id), "w") as f:
                f.write(state.model_dump_json(indent=2))
            return True
        except Exception as e:
            print(f"[FS Persistence] Error saving: {e}")
            return False

    def load_state(self, session_id: str) -> Optional[FlowState]:
        try:
            path = self._get_path(session_id)
            if not os.path.exists(path): return None
            with open(path, "r") as f:
                return FlowState(**json.load(f))
        except Exception:
            return None

class FileSystemAgentMemory(BaseAgentMemory):
    def __init__(self, base_dir: str = ".memories"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_user_path(self, user_id: str) -> str:
        safe_uid = "".join([c for c in user_id if c.isalnum() or c in "-_"])
        return os.path.join(self.base_dir, f"user_{safe_uid}.json")

    def _read(self, user_id: str):
        path = self._get_user_path(user_id)
        if not os.path.exists(path): return []
        try:
            with open(path, "r") as f:
                return [AgentMemoryItem(**x) for x in json.load(f)]
        except: return []

    def _write(self, user_id: str, items):
        with open(self._get_user_path(user_id), "w") as f:
            json.dump([x.model_dump(mode='json') for x in items], f, indent=2)

    def add_memory(self, item: AgentMemoryItem) -> bool:
        try:
            items = self._read(item.user_id)
            items.append(item)
            self._write(item.user_id, items)
            return True
        except: return False

    def get_memories(self, user_id: str, limit: int = 10):
        items = self._read(user_id)
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items[:limit]

    def search_memories(self, user_id: str, query: str):
        items = self._read(user_id)
        return [i for i in items if query.lower() in i.content.lower()]
