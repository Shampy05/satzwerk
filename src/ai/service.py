from typing import cast

from src.ai.exceptions import CardGenerationFailedException
from src.ai.graph import graph
from src.ai.schema import GermanCard
from src.ai.state import State


class AIService:
    @staticmethod
    async def generate_card(sentence: str) -> GermanCard:
        initial_state: State = {
            "sentence": sentence,
            "card": None,
            "is_valid": False,
            "critique": "",
            "iterations": 0,
        }

        final_state: State = cast(State, await graph.ainvoke(initial_state))

        card = final_state.get("card")

        if not card or not final_state.get("is_valid"):
            raise CardGenerationFailedException(
                message=f"Failed to generate a valid card after {final_state['iterations']} attempts."
            )

        return card
