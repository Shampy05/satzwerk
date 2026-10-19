from typing import Literal

from src.ai.state import State
from src.config import settings


def decide_after_deterministic(
    state: State,
) -> Literal["semantic_evaluator", "generator", "end"]:
    if state["is_valid"]:
        return "semantic_evaluator"
    if state["iterations"] >= settings.AI_MAX_ITERATIONS:
        return "end"
    return "generator"


def decide_after_semantic(state: State) -> Literal["generator", "end"]:
    if state["is_valid"] or state["iterations"] >= settings.AI_MAX_ITERATIONS:
        return "end"
    return "generator"
