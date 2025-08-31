from __future__ import annotations

from usb_pd_parser.config import Config
from usb_pd_parser.pdf_document import PDFDocument
from usb_pd_parser.toc_extractor import ToCExtractor


class _MockPDF(PDFDocument):
    def __init__(self, pages):
        self._pages = pages

    def num_pages(self) -> int:
        return len(self._pages)

    def load_all_text(self):
        return self._pages

    def load_pages_text(self, pages=None):
        if pages is None:
            return self._pages
        return [self._pages[p - 1] for p in pages]


def test_toc_parses_and_preserves_parents():
    # Page 1: ToC heading
    # Page 2: Lines with wrapped and nested items
    pages = [
        "TABLE OF CONTENTS",
        "2 Overview . . . . . . . . . . . . . . . . . . . . . . 10\n"
        "2.1 Protocol Summary . . . . . . . . . . . . . . . 11\n"
        "2.1.1 Source Role . . . . . . . . . . . . . . . . . 12\n"
        "2.1.1.1 Deep Child . . . . . . . . . . . . . . . . . 13",
        "Body starts here 1. Intro",
    ]
    pdf = _MockPDF(pages)
    cfg = Config()
    # Hint range to include page 1..2
    cfg.toc_start_hint = 1
    cfg.toc_end_hint = 2
    toc = ToCExtractor(cfg).extract(pdf, "Doc")
    ids = sorted([t["section_id"] for t in toc], key=lambda s: tuple(int(x) for x in s.split(".")))
    # Ensure parent preservation created missing parents if any (should already be present here)
    assert "2" in ids
    assert "2.1" in ids
    assert "2.1.1" in ids
    assert "2.1.1.1" in ids
