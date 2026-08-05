"""
Schema Module

Defines the structure and validation for support assistant response payloads.
"""

from typing import List
from pydantic import BaseModel, Field


class AnswerResponse(BaseModel):
    """
    Pydantic schema representing the validated response from the support assistant graph.
    """
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
