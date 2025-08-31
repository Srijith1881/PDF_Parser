from __future__ import annotations

from pathlib import Path

from usb_pd_parser.config import Config
from usb_pd_parser.pipeline import Pipeline
from usb_pd_parser.pdf_document import PDFDocument


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


def test_pipeline_end_to_end_tmp(tmp_path: Path, monkeypatch):
    # Craft ToC-like first two pages and simple body
    pages = [
        "Contents\n1 Introduction . . . . . . . . . . . . 3\n2 Overview . . . . . . . . . . . . . . 5\n2.1 Detail . . . . . . . . . . . . . . 7",
        "",
        "Page 3 - Intro text.",
        "Page 4 - filler.",
        "Page 5 - Overview text.",
        "Page 6 - filler.",
        "Page 7 - Detail text, end of doc.",
    ]
    # Monkeypatch PDFDocument used in Pipeline
    def _fake_pdf_ctor(path: str):
        return _MockPDF(pages)

    monkeypatch.setattr("usb_pd_parser.pipeline.PDFDocument", _fake_pdf_ctor)
    cfg = Config()
    cfg.toc_start_hint = 1
    cfg.toc_end_hint = 1
    out = Pipeline(cfg).run(
        pdf_path="dummy.pdf",
        doc_title="USB PD Spec",
        out_dir=tmp_path.as_posix(),
    )

    # Check files exist and not empty
    for k in ["toc", "sections", "metadata", "report"]:
        assert Path(out[k]).exists()
