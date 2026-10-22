import hashlib
from collections import Counter
from typing import cast

from pydantic import ValidationError
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from valkey.exceptions import ValkeyError

from src.ai.constants import CEFR_RANK, TAXONOMY, CEFRLevel, Language, PatternCode
from src.ai.exceptions import CardGenerationFailedException
from src.ai.graph import graph
from src.ai.llm import structured_prompt_llm
from src.ai.prompts import build_writing_prompt_messages
from src.ai.schema import (
    Analysis,
    EnrichedAnalysis,
    EnrichedGermanCard,
    GermanCard,
    LearnerProfile,
    WritingPromptResponse,
)
from src.ai.state import State
from src.ai.utils import locate_sentence
from src.auth.models import UserErrorLedger
from src.cache import valkey_client

DRAFT_CACHE_TTL_SECONDS = 86400


class AIService:
    @staticmethod
    def _draft_cache_key(
        sentence: str,
        cefr_level: CEFRLevel,
        language: Language = Language.DE,
    ) -> str:
        digest = hashlib.sha256(sentence.strip().encode("utf-8")).hexdigest()
        return f"ai:draft:{language}:{cefr_level}:{digest}"

    @staticmethod
    async def analyze_draft(
        sentence: str,
        learner: LearnerProfile | None = None,
        db: AsyncSession | None = None,
        is_revision: bool = False,
        repaired_patterns: list[PatternCode] | None = None,
    ) -> EnrichedAnalysis:
        if learner is None:
            learner = LearnerProfile()

        cache_key = AIService._draft_cache_key(
            sentence, learner.cefr_level, learner.language
        )
        analysis: Analysis | None = None

        try:
            cached_payload = await valkey_client.get(cache_key)
            if cached_payload:
                analysis = Analysis.model_validate_json(cached_payload)
        except (ValkeyError, ValidationError):
            analysis = None

        if analysis is None:
            initial_state: State = {
                "sentence": sentence,
                "analysis": None,
                "is_valid": False,
                "critique": "",
                "iterations": 0,
                "cefr_level": learner.cefr_level,
                "language": learner.language,
            }

            final_state: State = cast(State, await graph.ainvoke(initial_state))
            analysis = final_state.get("analysis")

            if not analysis or not final_state.get("is_valid"):
                raise CardGenerationFailedException(
                    message=f"Failed to generate a valid card after {final_state['iterations']} attempts."
                )

            try:
                await valkey_client.set(
                    cache_key,
                    analysis.model_dump_json(),
                    ex=DRAFT_CACHE_TTL_SECONDS,
                )
            except ValkeyError:
                pass

        if learner.user_id is not None and db is not None:
            if not is_revision and analysis.cards:
                await AIService.record_user_error(
                    db=db, user_id=learner.user_id, cards=analysis.cards
                )
            elif is_revision and repaired_patterns:
                remaining = {card.pattern_code for card in analysis.cards}
                healed = [code for code in repaired_patterns if code not in remaining]

                if healed:
                    await AIService.heal_user_errors(
                        db=db, user_id=learner.user_id, patterns=healed
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

    @staticmethod
    async def get_top_weaknesses(
        db: AsyncSession,
        user_id: int,
        user_cefr: CEFRLevel,
        language: Language = Language.DE,
    ) -> list[PatternCode]:
        stmt = select(UserErrorLedger).where(UserErrorLedger.user_id == user_id)
        result = await db.execute(stmt)

        rows = result.scalars().all()
        scores: dict[PatternCode, int] = {}
        user_rank = CEFR_RANK[user_cefr]

        for row in rows:
            try:
                code = PatternCode(row.pattern_code)
            except ValueError:
                continue
            meta = TAXONOMY[code]
            if meta["language"] != language or not meta["treatable"]:
                continue

            pattern_rank = CEFR_RANK[meta["cefr"]]
            if pattern_rank <= user_rank:
                scores[code] = row.error_count * 2
            else:
                scores[code] = row.error_count

        return sorted(scores, key=lambda code: scores[code], reverse=True)[:3]

    @staticmethod
    async def generate_writing_prompt(
        db: AsyncSession,
        user_id: int | None,
        user_cefr: CEFRLevel,
        language: Language = Language.DE,
    ) -> WritingPromptResponse:
        weaknesses = (
            await AIService.get_top_weaknesses(
                db=db, user_id=user_id, user_cefr=user_cefr, language=language
            )
            if user_id is not None
            else []
        )
        messages = build_writing_prompt_messages(
            cefr_level=user_cefr, target_patterns=weaknesses, language=language
        )
        return cast(
            WritingPromptResponse, await structured_prompt_llm.ainvoke(messages)
        )

    @staticmethod
    async def heal_user_errors(
        db: AsyncSession, user_id: int, patterns: list[PatternCode]
    ) -> None:
        if not patterns:
            return

        counts = Counter(patterns)
        for code, count in counts.items():
            await db.execute(
                update(UserErrorLedger)
                .where(
                    UserErrorLedger.user_id == user_id,
                    UserErrorLedger.pattern_code == code,
                )
                .values(error_count=UserErrorLedger.error_count - count)
            )

        await db.execute(
            delete(UserErrorLedger).where(
                UserErrorLedger.user_id == user_id,
                UserErrorLedger.error_count <= 0,
            )
        )

        await db.commit()
