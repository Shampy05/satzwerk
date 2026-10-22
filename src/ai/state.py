from typing import NotRequired, TypedDict

from src.ai.constants import CEFRLevel, Language
from src.ai.schema import Analysis


class State(TypedDict):
    sentence: str
    analysis: Analysis | None
    critique: str
    is_valid: bool
    iterations: int
    cefr_level: NotRequired[CEFRLevel]
    language: NotRequired[Language]
