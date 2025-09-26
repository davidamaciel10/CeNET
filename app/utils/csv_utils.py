from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence

from .paths import ensure_directory


def append_csv(path: Path, headers: Sequence[str], rows: Iterable[Sequence]) -> None:
    ensure_directory(path.parent)
    file_exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def write_csv(path: Path, headers: Sequence[str], rows: Iterable[Sequence]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
