# ============================================================================
# ug40_pipeline/dedupe.py
# ============================================================================
"""Ultra‑fast hashing helpers for duplicate paragraph detection."""
from xxhash import xxh3_64_hexdigest  # type: ignore[import]


def text_hash(text: str) -> str:  # noqa: D401 – simple wrapper
    """Return a 64‑bit hex digest of *text* (case‑sensitive)."""
    return xxh3_64_hexdigest(text)
