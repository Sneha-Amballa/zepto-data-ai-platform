"""
Pydantic schemas for the support assistant payloads.
"""

from typing import List
from pydantic import BaseModel, Field


class AnswerResponse(BaseModel):
    """Schema for validated support assistant response."""
    answer: str = Field(
        description="The customer support answer grounded in policy documents."
    )
    sources: List[str] = Field(
        description="List of document identifiers (e.g. ['doc_01.txt']) used to construct the answer."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score indicating alignment with document context, between 0.0 and 1.0."
    )
