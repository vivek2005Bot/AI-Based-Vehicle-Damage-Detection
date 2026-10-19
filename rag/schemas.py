"""Pydantic schemas for RAG knowledge ingestion and citation retrieval.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 12.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KnowledgeCitation(BaseModel):
    source_id: str
    document_title: str
    publisher: str
    section: str
    page_number: Optional[int] = None
    url: Optional[str] = None
    license_type: str = "Open Public Safety Standard / OEM Service Bulletin"


class StructuredGuidance(BaseModel):
    title: str = ""
    what_we_found: str = ""
    why_this_matters: str = ""
    what_you_should_do_now: str = ""
    can_i_keep_driving: str = ""
    what_mechanic_may_check: List[str] = Field(default_factory=list)
    technical_explanation: str = ""


class RetrievedPassage(BaseModel):
    passage_id: str
    citation: KnowledgeCitation
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    matched_damage_class: Optional[str] = None
    matched_dtc: Optional[str] = None
    guidance: Optional[StructuredGuidance] = None


class RAGRetrievalResult(BaseModel):
    status: str = Field(default="completed", description="completed, no_sources_available, or failed")
    query_used: str
    total_sources_searched: int = 0
    passages: List[RetrievedPassage] = Field(default_factory=list)
    citations: List[KnowledgeCitation] = Field(default_factory=list)
    summary_guidance: str = ""
    grounding_verified: bool = True
