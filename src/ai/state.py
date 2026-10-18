from typing import TypedDict

from src.ai.schema import GermanCard


class State(TypedDict):
    sentence: str
    card: GermanCard | None
    critique: str
    is_valid: bool
    iterations: int
