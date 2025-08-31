from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List


def write_jsonl(data: Iterable[dict], filename: str | Path) -> None:
    p = Path(filename)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def split_lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
