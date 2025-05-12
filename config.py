# ============================================================================
# ug40_pipeline/config.py
# ============================================================================
"""Centralised configuration & constants.

Environment variables override sensible defaults so the same code runs locally,
inside Google Colab, or in CI without edits.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Mapping

# ---- Paths -----------------------------------------------------------------
DRIVE_ROOT: Final[Path] = Path(
    os.getenv("DRIVE_ROOT", "/content/drive/MyDrive/UG40")
).expanduser()

MANIFEST_PATH: Final[Path] = Path(
    os.getenv("MANIFEST_PATH", DRIVE_ROOT / "metadata" / "manifest.sqlite")
)
MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---- Hugging Face -----------------------------------------------------------
HF_TOKEN: Final[str | None] = os.getenv("HF_TOKEN")  # personal‑access token
HF_REPO_ID: Final[str] = os.getenv("HF_REPO_ID", "Sunbird/ug40")

# ---- Category → schema model mapping ---------------------------------------
CATEGORY_MODELS: Final[Mapping[str, str]] = {
    "general_text": "GeneralText",
    "language_guides": "LanguageGuide",
    # add the rest as you implement them
}



