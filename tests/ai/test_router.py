from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.constants import CEFRLevel
from src.ai.schema import EnrichedAnalysis, LearnerProfile
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
