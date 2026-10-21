from typing import cast

from src.ai.exceptions import CardGenerationFailedException
from src.ai.graph import graph
from src.ai.schema import EnrichedAnalysis, EnrichedGermanCard
from src.ai.state import State
from src.ai.utils import locate_sentence


class AIService:
    @staticmethod
    async def analyze_draft(sentence: str) -> EnrichedAnalysis:
        initial_state: State = {
            "sentence": sentence,
            "analysis": None,
            "is_valid": False,
            "critique": "",
            "iterations": 0,
        }

        final_state: State = cast(State, await graph.ainvoke(initial_state))

        analysis = final_state.get("analysis")

        if not analysis or not final_state.get("is_valid"):
            raise CardGenerationFailedException(
                message=f"Failed to generate a valid card after {final_state['iterations']} attempts."
            )

        if not analysis.cards:
            return EnrichedAnalysis(
                cards=[],
                confirmed_hypotheses=analysis.confirmed_hypotheses,
            )

        enriched_cards = [
            EnrichedGermanCard.from_card(
                card, sentence_index=locate_sentence(text=sentence, quote=card.quote)
            )
            for card in analysis.cards
        ]

        return EnrichedAnalysis(
            cards=enriched_cards,
            confirmed_hypotheses=analysis.confirmed_hypotheses,
        )
