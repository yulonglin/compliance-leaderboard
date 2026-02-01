from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field


class ScoreLevel(IntEnum):
    ABSENT = 0
    MENTIONED = 1
    PARTIAL = 2
    THOROUGH = 3


class ScoringGuidance(BaseModel):
    absent: str = Field(description="What ABSENT (0) looks like for this requirement")
    mentioned: str = Field(description="What MENTIONED (1) looks like")
    partial: str = Field(description="What PARTIAL (2) looks like")
    thorough: str = Field(description="What THOROUGH (3) looks like")


class Requirement(BaseModel):
    id: str = Field(description="Unique identifier, e.g. CoP-1, STREAM-C1, ASL-1")
    framework: str = Field(description="EU Code of Practice | STREAM | Lab Safety Commitments")
    category: str = Field(description="Grouping within framework")
    short_name: str = Field(description="Brief label for display")
    description: str = Field(description="Full requirement text")
    scoring_guidance: ScoringGuidance
    gold_examples: list[str] = Field(
        description="Example passages that would score THOROUGH"
    )


class QuoteSpan(BaseModel):
    quote: str = Field(description="Verbatim quote from the chunk text")
    start: int = Field(description="Start character offset (0-indexed) in the chunk text")
    end: int = Field(description="End character offset (exclusive) in the chunk text")


class ClaimExtraction(BaseModel):
    relevant: bool = Field(description="Whether the chunk contains relevant information")
    claims: list[str] = Field(default_factory=list, description="Extracted claims")
    quotes: list[str] = Field(default_factory=list, description="Direct quotes or expanded snippets")
    quote_spans: list[QuoteSpan] = Field(
        default_factory=list,
        description="Quote spans extracted from the chunk text",
    )


class RequirementScore(BaseModel):
    requirement_id: str
    score: ScoreLevel
    justification: str = Field(description="2-3 sentence explanation of the score")
    evidence: list[str] = Field(description="Specific quotes supporting the score")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Model confidence in this score"
    )
    substantive: Optional[bool] = Field(
        default=None,
        description="Whether disclosure appears substantive (genuine detail) vs performative (checkbox compliance)",
    )
    substantive_reasoning: Optional[str] = Field(
        default=None,
        description="Brief explanation of substantive vs performative assessment",
    )


class ModelReport(BaseModel):
    model_name: str
    model_card_source: str
    scores: list[RequirementScore]
    cop_percentage: float
    stream_percentage: float
    lab_safety_percentage: float
    overall_percentage: float


class AggregatedRequirementInput(BaseModel):
    requirement: Requirement
    claims: list[str]
    quotes: list[str]
    model_name: str
    model_card_source: str


class ExtractionInput(BaseModel):
    requirement: Requirement
    chunk_text: str
    model_name: str
    model_card_source: str


class ValidationRow(BaseModel):
    rater_id: str
    model: str
    requirement_id: str
    score: Optional[int]
    justification: Optional[str]
    evidence_quote: Optional[str]
    minutes_spent: Optional[float]
