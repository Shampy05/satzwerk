from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.ai.schema import GermanCard

SYSTEM_PROMPT = (
    "You are a German SLA syntax analyser. Given a learner's sentence, identify:\n"
    "1. quote (L2): the exact broken words from the sentence.\n"
    "2. correction (L5): the corrected words.\n"
    "3. explanation (L4): a grammatical rule hint that MUST NOT contain any word from the correction"
)


def build_generator_messages(
    sentence: str, critique: str | None, previous_card: GermanCard | None = None
) -> list[BaseMessage]:
    user_content = f"Sentence: {sentence}"

    if previous_card and critique:
        user_content += (
            f"\n\nYour previous explanation was '{previous_card.explanation}'"
            f"\nCritique: {critique}"
        )
    return [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_content)]
