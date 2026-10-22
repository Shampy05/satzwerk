from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.constants import CEFRLevel, Language, PatternCode
from src.ai.schema import (
    Analysis,
    EnrichedAnalysis,
    GermanCard,
    LearnerProfile,
    WritingPromptResponse,
)
from src.ai.service import AIService
from src.auth.dependencies import get_optional_current_user
from src.auth.models import User
from src.auth.security import create_tokens


@pytest.mark.asyncio
class TestOptionalUserRouter:
    @patch("src.ai.service.AIService.analyze_draft", new_callable=AsyncMock)
    async def test_analyze_draft_anonymous_guest(
        self, mock_analyze: AsyncMock, client: AsyncClient
    ):
        mock_analyze.return_value = EnrichedAnalysis(
            cards=[], confirmed_hypotheses=[]
        )

        response = await client.post(
            "/ai/analyze-draft",
            json={"sentence": "Ich gehe heute nach Hause."},
        )

        assert response.status_code == 200
        mock_analyze.assert_called_once()
        _, kwargs = mock_analyze.call_args
        learner: LearnerProfile = kwargs["learner"]
        assert learner.user_id is None
        assert learner.cefr_level == CEFRLevel.A1

    @patch("src.ai.service.AIService.analyze_draft", new_callable=AsyncMock)
    async def test_analyze_draft_authenticated_user(
        self, mock_analyze: AsyncMock, client: AsyncClient, verified_user: User
    ):
        mock_analyze.return_value = EnrichedAnalysis(
            cards=[], confirmed_hypotheses=[]
        )
        access_token, _ = create_tokens(subject=verified_user.id)

        response = await client.post(
            "/ai/analyze-draft",
            json={"sentence": "Ich gehe heute nach Hause."},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        mock_analyze.assert_called_once()
        _, kwargs = mock_analyze.call_args
        learner: LearnerProfile = kwargs["learner"]
        assert learner.user_id == verified_user.id
        assert learner.cefr_level == verified_user.cefr_level

    @patch("src.ai.service.AIService.analyze_draft", new_callable=AsyncMock)
    async def test_analyze_draft_with_target_level_override(
        self, mock_analyze: AsyncMock, client: AsyncClient, verified_user: User
    ):
        mock_analyze.return_value = EnrichedAnalysis(
            cards=[], confirmed_hypotheses=[]
        )
        access_token, _ = create_tokens(subject=verified_user.id)

        response = await client.post(
            "/ai/analyze-draft",
            json={
                "sentence": "Ich gehe heute nach Hause.",
                "target_level": "B2",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        mock_analyze.assert_called_once()
        _, kwargs = mock_analyze.call_args
        learner: LearnerProfile = kwargs["learner"]
        assert learner.user_id == verified_user.id
        assert learner.cefr_level == CEFRLevel.B2

    @patch("src.ai.service.AIService.analyze_draft", new_callable=AsyncMock)
    async def test_analyze_draft_invalid_token_falls_back_to_guest(
        self, mock_analyze: AsyncMock, client: AsyncClient
    ):
        mock_analyze.return_value = EnrichedAnalysis(
            cards=[], confirmed_hypotheses=[]
        )

        response = await client.post(
            "/ai/analyze-draft",
            json={"sentence": "Ich gehe heute nach Hause."},
            headers={"Authorization": "Bearer not_a_valid_token_xyz"},
        )

        assert response.status_code == 200
        mock_analyze.assert_called_once()
        _, kwargs = mock_analyze.call_args
        learner: LearnerProfile = kwargs["learner"]
        assert learner.user_id is None
        assert learner.cefr_level == CEFRLevel.A1


@pytest.mark.asyncio
class TestGetOptionalCurrentUserDirect:
    async def test_none_token_returns_none(self, db_session: AsyncSession):
        result = await get_optional_current_user(token=None, db=db_session)
        assert result is None


@pytest.mark.asyncio
class TestErrorLedgerAndPrompts:
    async def test_ledger_upsert_and_weaknesses_endpoint(
        self, client: AsyncClient, db_session: AsyncSession, verified_user: User
    ):
        verified_user.cefr_level = CEFRLevel.B1
        await db_session.commit()

        draft_1_cards = [
            GermanCard(
                quote="a",
                pattern_code=PatternCode.KAS_GEN,
                explanation="hint",
                correction="b",
            ),
            GermanCard(
                quote="c",
                pattern_code=PatternCode.KAS_GEN,
                explanation="hint",
                correction="d",
            ),
            GermanCard(
                quote="e",
                pattern_code=PatternCode.WORTW,
                explanation="hint",
                correction="f",
            ),
        ]
        draft_2_cards = [
            GermanCard(
                quote="g",
                pattern_code=PatternCode.WO_V2,
                explanation="hint",
                correction="h",
            ),
            GermanCard(
                quote="i",
                pattern_code=PatternCode.WO_V2,
                explanation="hint",
                correction="j",
            ),
        ]

        await AIService.record_user_error(db_session, verified_user.id, draft_1_cards)
        await AIService.record_user_error(db_session, verified_user.id, draft_2_cards)

        access_token, _ = create_tokens(subject=verified_user.id)
        response = await client.get(
            "/ai/weaknesses",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json() == ["WO-V2", "KAS-GEN"]

    @patch("src.ai.service.structured_prompt_llm")
    async def test_writing_prompt_endpoint(
        self,
        mock_prompt_llm: AsyncMock,
        client: AsyncClient,
        db_session: AsyncSession,
        verified_user: User,
    ):
        verified_user.cefr_level = CEFRLevel.B1
        await db_session.commit()

        await AIService.record_user_error(
            db_session,
            verified_user.id,
            [
                GermanCard(
                    quote="zu den",
                    pattern_code=PatternCode.KAS_PREP,
                    explanation="hint",
                    correction="zum",
                )
            ],
        )

        mock_prompt_llm.ainvoke = AsyncMock(
            return_value=WritingPromptResponse(
                prompt="Tell a detective in 2 sentences why you went to the station at 3 AM using 'zu' or 'mit'.",
                target_patterns=[PatternCode.KAS_PREP],
            )
        )

        access_token, _ = create_tokens(subject=verified_user.id)
        response = await client.get(
            "/ai/writing_prompt",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["target_patterns"] == ["KAS-PREP"]
        assert "detective" in data["prompt"]
        mock_prompt_llm.ainvoke.assert_called_once()

    @patch("src.ai.service.graph")
    async def test_analyze_draft_valkey_cache_hit_and_revision_guard(
        self,
        mock_graph: AsyncMock,
        db_session: AsyncSession,
        verified_user: User,
    ):
        card = GermanCard(
            quote="zu den Bahnhof",
            pattern_code=PatternCode.KAS_PREP,
            explanation="This preposition requires the dative case.",
            correction="zum Bahnhof",
        )
        mock_graph.ainvoke = AsyncMock(
            return_value={
                "sentence": "Ich gehe zu den Bahnhof.",
                "analysis": Analysis(cards=[card], confirmed_hypotheses=[]),
                "is_valid": True,
                "critique": "",
                "iterations": 1,
            }
        )

        learner = LearnerProfile(user_id=verified_user.id, cefr_level=CEFRLevel.B1)

        # 1. First call (Cache MISS, is_revision=False) -> invokes graph + records 1 error in ledger
        res1 = await AIService.analyze_draft(
            sentence="Ich gehe zu den Bahnhof.",
            learner=learner,
            db=db_session,
            is_revision=False,
        )
        assert len(res1.cards) == 1
        assert res1.cards[0].sentence_index == 0
        assert mock_graph.ainvoke.call_count == 1

        # 2. Second call with is_revision=True (Cache HIT) -> skips graph AND skips ledger
        res2 = await AIService.analyze_draft(
            sentence="Ich gehe zu den Bahnhof.",
            learner=learner,
            db=db_session,
            is_revision=True,
        )
        assert len(res2.cards) == 1
        assert mock_graph.ainvoke.call_count == 1  # Still 1! Served from Valkey cache

        # 3. Verify ledger only recorded the initial draft (not the revision)
        weaknesses = await AIService.get_top_weaknesses(
            db_session, verified_user.id, CEFRLevel.B1
        )
        assert weaknesses == [PatternCode.KAS_PREP]

    @patch("src.ai.service.graph")
    async def test_analyze_draft_clean_draft_with_confirmed_hypothesis(
        self,
        mock_graph: AsyncMock,
        db_session: AsyncSession,
        verified_user: User,
    ):
        mock_graph.ainvoke = AsyncMock(
            return_value={
                "sentence": "Ich helfe ?dem Mann?.",
                "analysis": Analysis(cards=[], confirmed_hypotheses=["dem Mann"]),
                "is_valid": True,
                "critique": "",
                "iterations": 1,
            }
        )

        learner = LearnerProfile(user_id=verified_user.id, cefr_level=CEFRLevel.B1)
        res = await AIService.analyze_draft(
            sentence="Ich helfe ?dem Mann?.",
            learner=learner,
            db=db_session,
        )
        assert res.cards == []
        assert res.confirmed_hypotheses == ["dem Mann"]

    async def test_french_error_ledger_isolation_and_router(
        self, client: AsyncClient, db_session: AsyncSession, verified_user: User
    ):
        verified_user.cefr_level = CEFRLevel.B1
        await db_session.commit()

        # Record both German and French errors for the same user
        await AIService.record_user_error(
            db_session,
            verified_user.id,
            [
                GermanCard(
                    quote="zu den",
                    pattern_code=PatternCode.KAS_PREP,
                    explanation="dative required",
                    correction="zum",
                ),
                GermanCard(
                    quote="à le",
                    pattern_code=PatternCode.FR_PREP,
                    explanation="contraction required",
                    correction="au",
                ),
                GermanCard(
                    quote="ai allé",
                    pattern_code=PatternCode.FR_AUX,
                    explanation="être required",
                    correction="suis allé",
                ),
            ],
        )

        access_token, _ = create_tokens(subject=verified_user.id)

        # Query German weaknesses -> only German codes
        res_de = await client.get(
            "/ai/weaknesses?language=de",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert res_de.status_code == 200
        assert res_de.json() == ["KAS-PREP"]

        # Query French weaknesses -> only French codes
        res_fr = await client.get(
            "/ai/weaknesses?language=fr",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert res_fr.status_code == 200
        assert set(res_fr.json()) == {"FR-PREP", "FR-AUX"}

    @patch("src.ai.service.graph")
    async def test_error_ledger_healing_on_revision(
        self,
        mock_graph: AsyncMock,
        db_session: AsyncSession,
        verified_user: User,
    ):
        learner = LearnerProfile(user_id=verified_user.id, cefr_level=CEFRLevel.B1)

        # 1. Initial draft has 1 KAS-PREP error and 1 WO-VF error
        await AIService.record_user_error(
            db_session,
            verified_user.id,
            [
                GermanCard(
                    quote="zu den Bahnhof",
                    pattern_code=PatternCode.KAS_PREP,
                    explanation="dative required",
                    correction="zum Bahnhof",
                ),
                GermanCard(
                    quote="weil ich habe keine Zeit",
                    pattern_code=PatternCode.WO_VF,
                    explanation="verb at end",
                    correction="weil ich keine Zeit habe",
                ),
            ],
        )

        weaknesses_before = await AIService.get_top_weaknesses(
            db_session, verified_user.id, CEFRLevel.B1
        )
        assert set(weaknesses_before) == {PatternCode.KAS_PREP, PatternCode.WO_VF}

        # 2. Learner revises draft and fixes KAS-PREP (without L5 spoiler), while WO-VF remains
        wo_card = GermanCard(
            quote="weil ich habe keine Zeit",
            pattern_code=PatternCode.WO_VF,
            explanation="verb at end",
            correction="weil ich keine Zeit habe",
        )
        mock_graph.ainvoke = AsyncMock(
            return_value={
                "sentence": "Ich gehe zum Bahnhof, weil ich habe keine Zeit.",
                "analysis": Analysis(cards=[wo_card], confirmed_hypotheses=[]),
                "is_valid": True,
                "critique": "",
                "iterations": 1,
            }
        )

        await AIService.analyze_draft(
            sentence="Ich gehe zum Bahnhof, weil ich habe keine Zeit.",
            learner=learner,
            db=db_session,
            is_revision=True,
            repaired_patterns=[PatternCode.KAS_PREP, PatternCode.WO_VF],
        )

        # KAS-PREP should be healed (count 1 -> 0 -> deleted), leaving only WO-VF!
        weaknesses_after = await AIService.get_top_weaknesses(
            db_session, verified_user.id, CEFRLevel.B1
        )
        assert weaknesses_after == [PatternCode.WO_VF]




