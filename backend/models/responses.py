from pydantic import BaseModel
from typing import Any


class StartResponse(BaseModel):
    session_id: str
    current_level: int
    world_state: dict[str, Any]


class InputResponse(BaseModel):
    accepted: bool
    message: str


class DecisionResponse(BaseModel):
    accepted: bool
    pipeline_resumed: bool
