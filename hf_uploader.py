# ============================================================================
# ug40_pipeline/hf_uploader.py
# ============================================================================
"""Helpers around huggingface_hub.Dataset push-to-hub."""
from __future__ import annotations

from datasets import Dataset, DatasetDict, disable_caching  # type: ignore[import]
from huggingface_hub import HfApi, HfFolder  # type: ignore[import]

disable_caching()


class HFHelper:
    def __init__(self, token: str | None):
        self._token = token or HfFolder.get_token()
        if not self._token:
            raise RuntimeError("No Hugging Face token provided or found in cache")
        self._api = HfApi(token=self._token)

    # ------------------------------------------------------------------
    def ensure_repo(self, repo: str) -> None:
        if not self._api.repo_exists(repo, repo_type="dataset"):
            self._api.create_repo(repo, repo_type="dataset", private=False)

    # ------------------------------------------------------------------
    def push_split(self, repo: str, subset: str, ds: Dataset) -> None:
        self.ensure_repo(repo)
        ds.push_to_hub(
            repo_id=repo,
            split="train",
            token=self._token,
            config_name=subset
            # commit_message=f"auto‑update • {subset} • {len(ds):,} rows",
        )
