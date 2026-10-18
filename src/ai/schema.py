from pydantic import BaseModel, Field


class GermanCard(BaseModel):
    quote: str = Field(description="L2")
    correction: str = Field(description="L5")
    explanation: str = Field(description="L4")


class GenerateCardRequest(BaseModel):
    sentence: str
