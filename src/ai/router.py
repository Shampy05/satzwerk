from fastapi import APIRouter, status

import src.ai.service as ai_service
from src.ai.schema import EnrichedAnalysis, GenerateCardRequest

ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.post(
    "/analyze-draft",
    response_model=EnrichedAnalysis,
    status_code=status.HTTP_200_OK,
)
async def generate_card(payload: GenerateCardRequest):
    return await ai_service.AIService.analyze_draft(payload.sentence)
