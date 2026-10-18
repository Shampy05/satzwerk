from typing import Literal, cast

from src.ai.schema import GermanCard
from src.ai.llm import structured_llm
from src.ai.prompts import build_generator_messages
from src.ai.state import State
from src.config import settings


def generator(state: State):
    print("---Node Generator---")
    messages = build_generator_messages(
        sentence=state["sentence"],
        critique=state["critique"],
        previous_card=state["card"],
    )

    result: GermanCard = cast(GermanCard, structured_llm.invoke(messages))
    return {"card": result, "iterations": state["iterations"] + 1}


def evaluator(state: State):
    print("---Node Evaluator---")

    card = state["card"]

    if card is None:
        raise ValueError("Evaluator called before card was generated.")

    if card.correction.lower() in card.explanation.lower():
        return {
            "is_valid": False,
            "critique": (
                f"You leaked the answer '{card.correction}' inside your explanation! "
                "Rewrite that explanation without using that phrase."
            ),
        }

    return {"is_valid": True, "critique": ""}


def decide(state: State) -> Literal["generator", "end"]:
    if state["is_valid"] or state["iterations"] >= settings.AI_MAX_ITERATIONS:
        return "end"
    return "generator"
