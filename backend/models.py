from pydantic import BaseModel
from typing import Optional


class GameState(BaseModel):
    hp: int = 100
    max_hp: int = 100
    location: str = "unknown"
    inventory: list[str] = []
    story_node: str = "start"


class GameAction(BaseModel):
    action: str


class LLMResponse(BaseModel):
    narrative: str
    choices: list[str] = []
    state_change: dict = {}


class GameSession(BaseModel):
    id: str
    state: GameState
    history: list[dict] = []
