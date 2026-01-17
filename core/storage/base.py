from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# --- Data Models ---

class FlowState(BaseModel):
    """Represents the snapshot of a workflow execution."""
    session_id: str
    user_id: Optional[str]
    status: str
    data: Dict[str, Any]
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentMemoryItem(BaseModel):
    """Represents a single unit of memory/fact."""
    memory_id: str
    user_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

# --- Interfaces ---

class BaseStatePersistence(ABC):
    @abstractmethod
    def save_state(self, state: FlowState) -> bool: pass

    @abstractmethod
    def load_state(self, session_id: str) -> Optional[FlowState]: pass

class BaseAgentMemory(ABC):
    @abstractmethod
    def add_memory(self, item: AgentMemoryItem) -> bool: pass

    @abstractmethod
    def get_memories(self, user_id: str, limit: int = 10) -> List[AgentMemoryItem]: pass
    
    @abstractmethod
    def search_memories(self, user_id: str, query: str) -> List[AgentMemoryItem]: pass
