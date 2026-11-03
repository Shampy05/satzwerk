import litellm
from langchain_litellm import ChatLiteLLMRouter
from litellm.router import Router

from src.ai.schema import Analysis, SemanticEvaluation, WritingPromptResponse
from src.config import settings

# Silently drop parameters not supported by the model (e.g. reasoning_effort on non-o1 models)
litellm.drop_params = True


def _normalize_model(model: str, default_provider: str = "openai") -> str:
    cleaned = model.strip("'\"")
    return cleaned if "/" in cleaned else f"{default_provider}/{cleaned}"


llm_router = Router(
    model_list=[
        {
            "model_name": "generator",
            "litellm_params": {
                "model": _normalize_model(settings.OPENAI_LLM_MODEL),
                "temperature": settings.LLM_TEMPERATURE,
            },
        },
        {
            "model_name": "critic",
            "litellm_params": {
                "model": _normalize_model(settings.CRITIC_LLM_MODEL),
                "temperature": 0.0,
            },
        },
    ]
)

generator_llm = ChatLiteLLMRouter(
    router=llm_router,
    model="generator",
)
critic_llm = ChatLiteLLMRouter(router=llm_router, model="critic")

structured_generator_llm = generator_llm.with_structured_output(Analysis)
structured_critic_llm = critic_llm.with_structured_output(SemanticEvaluation)
structured_prompt_llm = generator_llm.with_structured_output(WritingPromptResponse)
