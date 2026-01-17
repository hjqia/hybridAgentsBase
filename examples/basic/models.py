from pydantic import BaseModel, Field
from typing import List

# --- Define your Data Models here ---

class ExampleResult(BaseModel):
    summary: str = Field(..., description="A summary of the finding.")
    confidence: float = Field(..., description="Confidence score between 0 and 1.")

class FinalReport(BaseModel):
    title: str
    points: List[str] = Field(default_factory=list)
