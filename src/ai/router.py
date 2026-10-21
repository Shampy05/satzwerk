from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

import src.ai.service as ai_service
from src.ai.demo_html import DEMO_HTML
from src.ai.schema import EnrichedAnalysis, GenerateCardRequest

ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.get("/demo", response_class=HTMLResponse)
async def demo_ui():
    return HTMLResponse(content=DEMO_HTML)


@ai_router.post(
    "/analyze-draft",
    response_model=EnrichedAnalysis,
    status_code=status.HTTP_200_OK,
)
async def generate_card(payload: GenerateCardRequest):
    return await ai_service.AIService.analyze_draft(payload.sentence)
