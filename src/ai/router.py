from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

import src.ai.service as ai_service
from src.ai.constants import CEFRLevel
from src.ai.demo_html import DEMO_HTML
from src.ai.schema import EnrichedAnalysis, GenerateCardRequest, LearnerProfile
from src.auth.dependencies import OptionalCurrentUser
from src.dependencies import DbDep

ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.get("/demo", response_class=HTMLResponse)
async def demo_ui():
    return HTMLResponse(content=DEMO_HTML)


@ai_router.post(
    "/analyze-draft",
    response_model=EnrichedAnalysis,
    status_code=status.HTTP_200_OK,
)
async def generate_card(
    payload: GenerateCardRequest, user: OptionalCurrentUser, db: DbDep
):
    cefr_level = payload.target_level or (
        user.cefr_level if user else CEFRLevel.A1
    )
    learner = (
        LearnerProfile(user_id=user.id, cefr_level=cefr_level)
        if user
        else LearnerProfile(cefr_level=cefr_level)
    )
    return await ai_service.AIService.analyze_draft(
        sentence=payload.sentence,
        learner=learner,
        db=db,
    )
