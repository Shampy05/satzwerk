from pydantic import BaseModel, Field

from src.ai.constants import PatternCode


class GermanCard(BaseModel):
    quote: str = Field(description="L2: The exact broken words from the sentence")
    pattern_code: PatternCode = Field(
        description="L3: Exactly one error category code from the allowed taxonomy"
    )
    explanation: str = Field(
        description="L4: Pedagogical rule hint that MUST NOT contain any words from the correction"
    )
    correction: str = Field(description="L5: The corrected words")


class EnrichedGermanCard(GermanCard):
    sentence_index: int = Field(
        description="L1: Zero-indexed position of the sentence containing the error"
    )

    @classmethod
    def from_card(cls, card: GermanCard, sentence_index: int) -> "EnrichedGermanCard":
        return cls(**card.model_dump(), sentence_index=sentence_index)


class GenerateCardRequest(BaseModel):
    sentence: str


class Analysis(BaseModel):
    cards: list[GermanCard] = Field(
        description="List of error cards detected in the sentence"
    )


class EnrichedAnalysis(BaseModel):
    cards: list[EnrichedGermanCard] = Field(
        description="List of all detected error cards with sentence indices"
    )


class SemanticEvaluation(BaseModel):
    is_valid: bool = Field(
        description="True only if all semantic checks pass with zero issues"
    )
    critiques: list[str] = Field(
        description="List of specific critiques if is_valid is False; empty list is is_valid is True"
    )
