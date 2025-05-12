# ============================================================================
# ug40_pipeline/manifests.py
# ============================================================================
"""Lightweight SQLite manifest so the pipeline runs incrementally."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Iterable, Sequence

from sqlmodel import SQLModel, Field, Session, create_engine, select

# ---------------------------------------------------------------------------
class File(SQLModel, table=True):  # type: ignore[arg-type]
    file_id: str = Field(primary_key=True)
    lang: str
    subset: str
    md5: str
    processed_at: _dt.datetime


class TextHash(SQLModel, table=True):  # type: ignore[arg-type]
    text_hash: str = Field(primary_key=True)
    lang: str
    subset: str


class Manifest:
    """Typed façade over SQLite storage."""

    def __init__(self, db_path: Path) -> None:
        self._engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(self._engine)

    # ---- file‑level bookkeeping -------------------------------------------
    def seen_file(self, file_id: str, md5: str) -> bool:
        with Session(self._engine) as s:
            stmt = select(File).where(File.file_id == file_id)
            rec: File | None = s.exec(stmt).one_or_none()
            return rec is not None and rec.md5 == md5

    def upsert_file(self, file_id: str, lang: str, subset: str, md5: str) -> None:
        with Session(self._engine) as s:
            rec = File(file_id=file_id, lang=lang, subset=subset, md5=md5, processed_at=_dt.datetime.utcnow())
            s.merge(rec)
            s.commit()

    # ---- text‑level de‑duplication ----------------------------------------
    def is_duplicate_text(self, text_hash: str) -> bool:
        with Session(self._engine) as s:
            return s.get(TextHash, text_hash) is not None

    def add_text_hashes(self, rows: Iterable[TextHash]) -> None:
        with Session(self._engine) as s:
            s.add_all(rows)
            s.commit()
