from fastapi import APIRouter, status

import src.ai.service as ai_service
from src.ai.schema import GenerateCardRequest, GermanCard

ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.post(
    "/generate-card", response_model=GermanCard, status_code=status.HTTP_200_OK
)
async def generate_card(payload: GenerateCardRequest):
    return await ai_service.AIService.generate_card(payload.sentence)
