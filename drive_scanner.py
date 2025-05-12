# ============================================================================
# ug40_pipeline/drive_scanner.py
# ============================================================================
"""Google Drive discovery helpers.

This module relies on Google Drive API v3. In Colab you must first run:

```python
from google.colab import auth
auth.authenticate_user()
```

and then install the client with `pip install -q --upgrade google-api-python-client`.
"""
from __future__ import annotations

import itertools as _it
import os
from dataclasses import dataclass
from typing import Iterator

from googleapiclient.discovery import build  # type: ignore[import]
from googleapiclient.errors import HttpError  # type: ignore[import]

_GDRIVE_FIELDS = "id, name, md5Checksum, mimeType, parents"
_FOLDER_MIME = "application/vnd.google-apps.folder"


@dataclass(frozen=True)
class DriveFile:
    id: str
    name: str
    md5: str
    mime: str
    parents: list[str]


class DriveScanner:
    def __init__(self, root_folder_id: str | None = None) -> None:
        # If *root_folder_id* is None we assume DRIVE_ROOT path is mounted locally.
        self._svc = build("drive", "v3", cache_discovery=False)
        self._root = root_folder_id

    # ---------------------------------------------------------------------
    def iter_files(self) -> Iterator[DriveFile]:
        """Yield files recursively under *root_folder_id* (or all drive)."""
        page_token: str | None = None
        query = f"'{self._root}' in parents" if self._root else None
        while True:
            try:
                resp = (
                    self._svc.files()
                    .list(
                        q=query,
                        fields=f"nextPageToken, files({_GDRIVE_FIELDS})",
                        pageToken=page_token,
                    )
                    .execute()
                )
            except HttpError as e:  # pragma: no cover – just bubble up
                raise RuntimeError(f"Drive API error: {e}") from e
            for f in resp.get("files", []):
                yield DriveFile(
                    id=f["id"],
                    name=f["name"],
                    md5=f.get("md5Checksum", ""),
                    mime=f["mimeType"],
                    parents=f.get("parents", []),
                )
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    # Optional helper ------------------------------------------------------
    def walk_tree(self) -> Iterator[tuple[str, DriveFile]]:
        """Yield (drive_path, file) pairs so callers know language/subset."""
        # Build parent lookup lazily because Drive API does not give path outright.
        parents: dict[str, DriveFile] = {}
        for f in self.iter_files():
            for p in f.parents:
                parents.setdefault(p, None)
            # store file itself so we can query later
            parents[f.id] = f

        def build_path(fid: str) -> list[str]:  # noqa: WPS430 – nested
            node = parents.get(fid)
            if node is None or not node.parents:
                return [node.name] if node else []
            return build_path(node.parents[0]) + [node.name]

        for f in parents.values():
            if f and f.mime != _FOLDER_MIME:
                yield "/".join(build_path(f.id)), f

