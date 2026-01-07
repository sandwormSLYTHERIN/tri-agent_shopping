from pydantic import BaseModel
from typing import Literal

class AgentResponse(BaseModel):
    type: Literal["order", "complaint", "product"]
    message: str
    action_taken: str
    confidence: Literal["high", "medium", "low"]
