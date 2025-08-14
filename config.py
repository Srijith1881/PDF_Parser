# config.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class Config:
    # If you know the ToC span, set these; otherwise leave None to auto-detect
    toc_start_hint: Optional[int] = None     # e.g., 13
    toc_end_hint: Optional[int] = None       # e.g., 34

    # Fallback if auto-detect fails
    toc_default_pages: int = 40

    # Regex for classic dotted-leader ToC lines
    toc_regex: str = r'^(\d+(?:\.\d+)*)(\s+)([^\n.]+?)(?:\.+\s+)(\d+)$'
    table_regex: str = r'\bTable\s+\d+(?:-\d+)?\b'
    figure_regex: str = r'\bFigure\s+\d+(?:-\d+)?\b'

    # Phrases to detect ToC block boundaries and exclude false positives
    toc_heading_keywords: List[str] = field(default_factory=lambda: [
        "table of contents", "contents"
    ])
    toc_exclude_page_headings: List[str] = field(default_factory=lambda: [
        "revision history", "document history", "change log", "errata"
    ])

    metadata_regexes: Dict = None

    # output file names (can be overridden)
    toc_jsonl: str = "usb_pd_toc.jsonl"
    sections_jsonl: str = "usb_pd_spec.jsonl"
    metadata_jsonl: str = "usb_pd_metadata.jsonl"
    validation_report: str = "validation_report.xlsx"

    def __post_init__(self):
        self.metadata_regexes = {
            'table': self.table_regex,
            'figure': self.figure_regex
        }
