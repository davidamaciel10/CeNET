from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Iterable

INVALID_FILENAME_CHARS = r"[^A-Za-z0-9._-]"


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def safe_filename(value: str, default: str = "archivo") -> str:
    if not value:
        value = default
    value = normalize_text(value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ", "_")
    value = re.sub(INVALID_FILENAME_CHARS, "", value)
    return value or default


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    counter = 2
    while True:
        candidate = base_path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def iter_files(directory: Path, patterns: Iterable[str] | None = None):
    if patterns is None:
        patterns = ["*"]
    for pattern in patterns:
        yield from directory.glob(pattern)
