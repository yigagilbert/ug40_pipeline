# ============================================================================
# ug40_pipeline/transformers.py
# ============================================================================
"""Pure‑function text transformations."""
from __future__ import annotations

import re
from typing import Iterable

import markdown2  # type: ignore[import]

_PAR_SPLIT_RE = re.compile(r"\n{2,}")


def strip_markdown(md: str) -> str:
    """Convert *md* markdown to plain text."""
    html = markdown2.markdown(md)
    # naive but effective: remove all <tags>
    return re.sub(r"<[^>]+>", "", html)


def paragraph_split(text: str) -> list[str]:
    """Return list of non‑empty paragraphs."""
    return [p.strip() for p in _PAR_SPLIT_RE.split(text) if p.strip()]


def split_and_clean_general(md_text: str) -> list[str]:
    """Markdown → plain paragraphs suitable for *general_text* subset."""
    return paragraph_split(strip_markdown(md_text))

