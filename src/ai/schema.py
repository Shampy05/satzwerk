from pydantic import BaseModel, Field

from src.ai.constants import CEFRLevel, Language, PatternCode


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
    target_level: CEFRLevel | None = None
    language: Language | None = None
    is_revision: bool = False
    repaired_patterns: list[PatternCode] = []


class Analysis(BaseModel):
    cards: list[GermanCard] = Field(
        description="List of error cards detected in the sentence"
    )
    confirmed_hypotheses: list[str] = Field(
        description="List of words marked with ? in the draft that are grammatically correct"
    )


class EnrichedAnalysis(BaseModel):
    cards: list[EnrichedGermanCard] = Field(
        description="List of all detected error cards with sentence indices"
    )
    confirmed_hypotheses: list[str] = Field(
        description="List of words marked with ? in the draft that are grammatically correct"
    )


class SemanticEvaluation(BaseModel):
    critiques: list[str] = Field(
        description="List of specific rule violations found; MUST be an empty list [] if all 3 rules pass"
    )
    is_valid: bool = Field(
        description="True if critiques is empty []; False only if critiques is non-empty"
    )


class LearnerProfile(BaseModel):
    user_id: int | None = None
    cefr_level: CEFRLevel = CEFRLevel.A1
    language: Language = Language.DE


class WritingPromptResponse(BaseModel):
    prompt: str = Field(
        description="A short writing task in English with specific target-language grammar constraints for the learner"
    )
    target_patterns: list[PatternCode] = Field(
        description="The grammar pattern codes targetted by this writing prompt"
    )
