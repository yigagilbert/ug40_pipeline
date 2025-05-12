# Ug40 Pipeline

An incremental, **single‑command** pipeline for turning raw text stored on Google Drive into clean, de‑duplicated Hugging Face datasets covering 40+ Ugandan languages.

```
ug40-pipeline run --drive-root /content/drive/MyDrive/UG40 \
                 --subsets general_text,language_guides \
                 --hf-repo Sunbird/ug40
```

---

## ✨ Features

|                          | What it does                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| **Drive auto‑discovery** | Walks or queries Google Drive, detects *new or modified* files via file‑ID + MD5, so nothing is missed. |
| **Incremental runs**     | Skips previously processed content; typical re‑runs finish in seconds.                                  |
| **Per‑paragraph dedupe** | xxHash‑64 fingerprinting prevents accidental duplicates across contributors or categories.              |
| **Strict schemas**       | Pydantic v2 models enforce one canonical JSON layout per category (general\_text, language\_guides, …). |
| **Colab‑friendly**       | Works out of the box in Google Colab or any local Python ≥3.10.                                         |
| **One‑shot upload**      | Publishes or updates a dataset repo on Hugging Face in a single atomic push.                            |

---

## 📂 Drive Folder Convention

```
UG40/
│
├── metadata/manifest.sqlite   # created automatically
├── lug/
│   ├── general_text/          # .txt / .md files
│   └── language_guides/
└── toh/
    └── …
```

*Add new languages or categories simply by creating the corresponding folders and dropping files in.*

---

## 🚀 Quick Start (Colab)

```python
!pip install -q ug40-pipeline
from google.colab import auth, drive
auth.authenticate_user()                 # Google & HF tokens

drive.mount('/content/drive')
!ug40-pipeline run --drive-root /content/drive/MyDrive/UG40 \
                   --subsets general_text,language_guides \
                   --hf-repo Sunbird/ug40
```

---

## 🛠️ Development

```bash
poetry install  # or `pip install -e .[dev]`
pytest          # run tests
ruff check .    # lint
mypy .          # type‑check
```

---

## 🔄 Extending to New Categories

1. Add a Pydantic model in `ug40_pipeline/schema.py`.
2. Implement parsing logic in `transformers.py` if needed.
3. List the subset in `config.CATEGORY_MODELS`.

That’s it—discovery, deduplication, and HF upload already work.

---
