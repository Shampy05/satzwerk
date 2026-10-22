from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

import src.ai.service as ai_service
from src.ai.constants import CEFRLevel, Language, PatternCode
from src.ai.demo_html import DEMO_HTML
from src.ai.schema import (
    EnrichedAnalysis,
    GenerateCardRequest,
    LearnerProfile,
    WritingPromptResponse,
)
from src.auth.dependencies import CurrentUser, OptionalCurrentUser
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
    cefr_level = payload.target_level or (user.cefr_level if user else CEFRLevel.A1)
    language = payload.language or (user.target_language if user else Language.DE)
    learner = (
        LearnerProfile(user_id=user.id, cefr_level=cefr_level, language=language)
        if user
        else LearnerProfile(cefr_level=cefr_level, language=language)
    )
    return await ai_service.AIService.analyze_draft(
        sentence=payload.sentence,
        learner=learner,
        db=db,
        is_revision=payload.is_revision,
        repaired_patterns=payload.repaired_patterns,
    )


@ai_router.get(
    "/weaknesses", response_model=list[PatternCode], status_code=status.HTTP_200_OK
)
async def get_user_weaknesses(
    user: CurrentUser,
    db: DbDep,
    language: Language | None = None,
):
    active_lang = language or user.target_language
    return await ai_service.AIService.get_top_weaknesses(
        db=db, user_id=user.id, user_cefr=user.cefr_level, language=active_lang
    )


@ai_router.get(
    "/writing_prompt",
    response_model=WritingPromptResponse,
    status_code=status.HTTP_200_OK,
)
@ai_router.get(
    "/writing-prompt",
    response_model=WritingPromptResponse,
    status_code=status.HTTP_200_OK,
)
async def get_writing_prompt(
    user: OptionalCurrentUser,
    db: DbDep,
    target_level: CEFRLevel | None = None,
    language: Language | None = None,
):
    cefr_level = target_level or (user.cefr_level if user else CEFRLevel.A1)
    active_lang = language or (user.target_language if user else Language.DE)
    return await ai_service.AIService.generate_writing_prompt(
        db=db,
        user_id=user.id if user else None,
        user_cefr=cefr_level,
        language=active_lang,
    )
