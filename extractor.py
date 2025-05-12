# ============================================================================
# ug40_pipeline/extractor.py
# ============================================================================
"""File loading and Unicode normalisation."""
from __future__ import annotations

from pathlib import Path

import unicodedata as _ud


def read_text(path: Path) -> str:
    """Load utf‑8 (or best‑guess) text file, strip BOM and normalise."""
    raw = path.read_bytes()
    # Try utf‑8 first, fall back to latin‑1 so we *never* crash – we normalise later.
    for enc in ("utf‑8", "utf‑8‑sig", "latin‑1"):
        try:
            txt = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError("All decoders failed", b"", 0, 1, "unknown encoding")

    # Normalise to NFC to keep accents consistent.
    return _ud.normalize("NFC", txt)