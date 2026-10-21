from langchain_litellm import ChatLiteLLMRouter
from litellm.router import Router

from src.ai.schema import Analysis, SemanticEvaluation, WritingPromptResponse
from src.config import settings

llm_router = Router(
    model_list=[
        {
            "model_name": "generator",
            "litellm_params": {
                "model": settings.OPENAI_LLM_MODEL,
                "temperature": settings.LLM_TEMPERATURE,
                "reasoning_effort": "minimal",
            },
        },
        {
            "model_name": "critic",
            "litellm_params": {
                "model": settings.CRITIC_LLM_MODEL,
                "temperature": 0.0,
            },
        },
    ]
)

generator_llm = ChatLiteLLMRouter(
    router=llm_router,
    model="generator",
    model_kwargs={"reasoning_effort": "minimal"},
)
critic_llm = ChatLiteLLMRouter(router=llm_router, model="critic")

structured_generator_llm = generator_llm.with_structured_output(Analysis)
structured_critic_llm = critic_llm.with_structured_output(SemanticEvaluation)
structured_prompt_llm = generator_llm.with_structured_output(WritingPromptResponse)
