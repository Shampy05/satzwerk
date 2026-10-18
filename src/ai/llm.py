from langchain_litellm import ChatLiteLLM

from src.ai.schema import GermanCard
from src.config import settings

llm = ChatLiteLLM(model=settings.OPENAI_LLM_MODEL, temperature=settings.LLM_TEMPERATURE)

structured_llm = llm.with_structured_output(GermanCard)
