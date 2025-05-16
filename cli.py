# ============================================================================
# ug40_pipeline/cli.py
# ============================================================================
"""Typer‑based command‑line interface."""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Annotated

import typer
from datasets import Dataset  # type: ignore[import]

from . import config as C
from .dedupe import text_hash
from .extractor import read_text
from .manifests import Manifest, TextHash
from .schema import GeneralText, LanguageGuide  # extend as you add schemas
from .transformers import split_and_clean_general, strip_markdown
from .hf_uploader import HFHelper

app = typer.Typer(add_completion=False)


def _infer_lang_subset(rel_path: str) -> tuple[str, str]:
    # Expect path like "lug/general_text/foo.txt"
    lang, subset, *_ = rel_path.split("/", 2)
    return lang, subset


@app.command()
def run(
    drive_root: Annotated[str, typer.Option(help="Mounted drive root path")] = str(C.DRIVE_ROOT),
    subsets: Annotated[str, typer.Option(help="Comma‑separated subset names")] = "general_text,language_guides",
    hf_repo: Annotated[str, typer.Option(help="Target HF dataset repo id")] = C.HF_REPO_ID,
):
    """Discover, process, deduplicate and upload new data in *subsets*."""
    drive_root = Path(drive_root)
    # Ensure metadata directory exists
    metadata_dir = drive_root / 'metadata'
    metadata_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = metadata_dir / 'manifest.sqlite'
    typer.echo(f"Using manifest at: {manifest_path}")
    wanted = {s.strip() for s in subsets.split(",") if s.strip()}
    # manifest = Manifest(C.MANIFEST_PATH)
    manifest = Manifest(str(manifest_path))
    hf = HFHelper(C.HF_TOKEN)

    # Walk local drive (mounted) instead of Drive API: simpler & free quota.
    new_rows: list[dict] = []
    for path in drive_root.rglob("*"):
        if path.is_dir() or path.suffix not in {".txt", ".md"}:
            continue
        rel = path.relative_to(drive_root).as_posix()
        lang, subset = _infer_lang_subset(rel)
        if subset not in wanted:
            continue
        md5 = path.stat().st_mtime_ns.to_bytes(8, "little").hex()  # crude but cheap
        file_id = rel  # when local, use path as id
        if manifest.seen_file(file_id, md5):
            continue  # already processed at same mtime
        content = read_text(path)
        if subset == "general_text":
            paragraphs = split_and_clean_general(content)
            for p in paragraphs:
                h = text_hash(p)
                if manifest.is_duplicate_text(h):
                    continue
                new_rows.append(GeneralText(text=p, language=lang).model_dump())
                manifest.add_text_hashes([TextHash(text_hash=h, lang=lang, subset=subset)])
        elif subset == "language_guides":
            guide = LanguageGuide(text=strip_markdown(content), language=lang)
            h = text_hash(guide.text)
            if not manifest.is_duplicate_text(h):
                new_rows.append(guide.model_dump())
                manifest.add_text_hashes([TextHash(text_hash=h, lang=lang, subset=subset)])
        manifest.upsert_file(file_id, lang, subset, md5)

    if not new_rows:
        typer.echo("✔ No new data – dataset already up‑to‑date.")
        raise typer.Exit()

    ds = Dataset.from_list(new_rows)
    hf.push_split(hf_repo, "+".join(sorted(wanted)), ds)
    typer.echo(f"⬆ Uploaded {len(ds):,} new rows to https://huggingface.co/datasets/{hf_repo}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    app()
