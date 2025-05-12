# ============================================================================
# ug40_pipeline/__init__.py
# ============================================================================
"""Uganda‑40 language corpus processing pipeline."""

from importlib import metadata as _metadata

__version__: str = _metadata.version(__name__.replace("_", "-")) if False else "0.1.0"

# Convenient re‑export so users can simply `python -m ug40_pipeline run ...`
from .cli import app  # noqa: E402  pylint: disable=wrong-import-position

__all__ = ["app", "__version__"]