from typing import TypedDict

from src.ai.schema import Analysis


class State(TypedDict):
    sentence: str
    analysis: Analysis | None
    critique: str
    is_valid: bool
    iterations: int
