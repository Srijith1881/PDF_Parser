from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .config import Config
from .metadata_extractor import MetadataExtractor
from .pdf_document import PDFDocument
from .section_extractor import SectionExtractor
from .toc_extractor import ToCExtractor
from .utils import write_jsonl
from .validator import Validator


@dataclass
class Pipeline:
    cfg: Config

    def run(
        self,
        pdf_path: str,
        doc_title: str,
        out_dir: str = ".",
        toc_start: int | None = None,
        toc_end: int | None = None,
        toc_pages: int | None = None,   # added
        use_llm: bool = False,          # added
    ) -> Dict[str, str]:
        """
        Runs the full pipeline:
        - Extract ToC
        - Extract Sections
        - Extract Metadata
        - Validate results & generate report
        """

        pdf = PDFDocument(pdf_path)

        toc = ToCExtractor(self.cfg).extract(
            pdf, doc_title, toc_start=toc_start, toc_end=toc_end
        )
        sections = SectionExtractor().extract(pdf, toc)
        metadata = MetadataExtractor(self.cfg).extract(pdf, doc_title)

        out = {
            "toc": str(Path(out_dir, self.cfg.toc_jsonl)),
            "sections": str(Path(out_dir, self.cfg.sections_jsonl)),
            "metadata": str(Path(out_dir, self.cfg.metadata_jsonl)),
            "report": str(Path(out_dir, self.cfg.validation_report)),
        }

        Path(out_dir).mkdir(parents=True, exist_ok=True)

        write_jsonl(toc, out["toc"])
        write_jsonl(sections, out["sections"])
        write_jsonl(metadata, out["metadata"])

        results = Validator().validate(toc, sections, metadata)
        Validator().write_excel_report(results, out["report"])

        return out


# -------------------------
# Convenience wrapper so server.py can call run_pipeline()
# -------------------------
def run_pipeline(
    pdf_path: str,
    doc_title: str,
    out_dir: str,
    toc_start: int | None = None,
    toc_end: int | None = None,
) -> dict:
    cfg = Config()
    pipeline = Pipeline(cfg)
    return pipeline.run(
        pdf_path=pdf_path,
        doc_title=doc_title,
        out_dir=out_dir,
        toc_start=toc_start,
        toc_end=toc_end,
    )

