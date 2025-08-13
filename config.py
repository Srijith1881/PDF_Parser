
from dataclasses import dataclass

@dataclass
class Config:
    toc_default_pages: int = 40          # read first N pages for ToC by default
    toc_regex: str = r'^(\d+(?:\.\d+)*)(\s+)([^\n.]+?)(?:\.+\s+)(\d+)$'
    table_regex: str = r'\bTable\s+\d+(?:-\d+)?\b'
    figure_regex: str = r'\bFigure\s+\d+(?:-\d+)?\b'
    metadata_regexes: dict = None

    def __post_init__(self):
        self.metadata_regexes = {
            'table': self.table_regex,
            'figure': self.figure_regex
        }

    # output file names (can be overridden)
    toc_jsonl: str = "usb_pd_toc.jsonl"
    sections_jsonl: str = "usb_pd_spec.jsonl"
    metadata_jsonl: str = "usb_pd_metadata.jsonl"
    validation_report: str = "validation_report.xlsx"
