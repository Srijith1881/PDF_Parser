from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Config:
    # Known or hinted ToC span (optional; auto-detect if None)
    toc_start_hint: Optional[int] = None
    toc_end_hint: Optional[int] = None

    # Fallback pages to scan when auto-detect fails
    toc_default_pages: int = 40
    max_scan_pages: int = 120

    # ToC detection helpers
    toc_heading_keywords: List[str] = field(
        default_factory=lambda: ["table of contents", "contents"]
    )
    toc_exclude_page_headings: List[str] = field(
        default_factory=lambda: [
            "revision history",
            "document history",
            "change log",
            "errata",
        ]
    )

    # Regexes
    toc_regex: str = r"^(\d+(?:\.\d+)*)(\s+)([^\n.]+?)(?:\.+\s+)(\d+)$"
    table_regex: str = r"\bTable\s+\d+(?:-\d+)?\b"
    figure_regex: str = r"\bFigure\s+\d+(?:-\d+)?\b"

    metadata_regexes: Dict[str, str] = field(init=False)

    # Outputs
    toc_jsonl: str = "usb_pd_toc.jsonl"
    sections_jsonl: str = "usb_pd_spec.jsonl"
    metadata_jsonl: str = "usb_pd_metadata.jsonl"
    validation_report: str = "validation_report.xlsx"

    def __post_init__(self) -> None:
        self.metadata_regexes = {
            "table": self.table_regex,
            "figure": self.figure_regex,
        }
