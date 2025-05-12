# ============================================================================
# ug40_pipeline/schema.py
# ============================================================================
"""Pydantic v2 models defining each dataset row."""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, constr


class _BaseRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    language: constr(min_length=2, max_length=5) = Field(..., description="ISO‑639‑3 code")
    source_name: str | None = Field(None, description="Optional human‑readable provenance")


class GeneralText(_BaseRow):
    text: str = Field(..., description="Cleaned paragraph of running text")


class LanguageGuide(_BaseRow):
    content: str = Field(..., description="Full guide text as single blob")

