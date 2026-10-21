from collections import Counter
from typing import cast

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.exceptions import CardGenerationFailedException
from src.ai.graph import graph
from src.ai.schema import (
    EnrichedAnalysis,
    EnrichedGermanCard,
    GermanCard,
    LearnerProfile,
)
from src.ai.state import State
from src.ai.utils import locate_sentence
from src.auth.models import UserErrorLedger


class AIService:
    @staticmethod
    async def analyze_draft(
        sentence: str,
        learner: LearnerProfile = LearnerProfile(),
        db: AsyncSession | None = None,
    ) -> EnrichedAnalysis:
        initial_state: State = {
            "sentence": sentence,
            "analysis": None,
            "is_valid": False,
            "critique": "",
            "iterations": 0,
            "cefr_level": learner.cefr_level,
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

        if learner.user_id is not None and db is not None:
            await AIService.record_user_error(
                db=db, user_id=learner.user_id, cards=analysis.cards
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

    @staticmethod
    async def record_user_error(
        db: AsyncSession, user_id: int, cards: list[GermanCard]
    ) -> None:
        if not cards:
            return

        counts = Counter(card.pattern_code for card in cards)

        stmt = pg_insert(UserErrorLedger).values(
            [
                {
                    "user_id": user_id,
                    "pattern_code": code,
                    "error_count": count,
                    "last_error_at": func.now(),
                }
                for code, count in counts.items()
            ]
        )

        stmt = stmt.on_conflict_do_update(
            constraint="uq_user_pattern",
            set_={
                "error_count": UserErrorLedger.error_count + stmt.excluded.error_count,
                "last_error_at": func.now(),
            },
        )

        await db.execute(stmt)
        await db.commit()
