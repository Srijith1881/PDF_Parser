from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from .config import Config
from .pdf_document import PDFDocument


@dataclass
class MetadataExtractor:
    cfg: Config

    def extract(self, pdf: PDFDocument, doc_title: str) -> List[Dict]:
        """Heuristically find 'Table x-y' and 'Figure x-y' across pages."""
        patterns = {k: re.compile(v) for k, v in self.cfg.metadata_regexes.items()}
        results: List[Dict] = []
        for pno, text in enumerate(pdf.load_all_text(), start=1):
            for kind, pat in patterns.items():
                for m in pat.finditer(text or ""):
                    ident = m.group(0)
                    title = ident  # Without true captions we reuse ident
                    results.append(
                        {
                            "doc_title": doc_title,
                            "type": kind,
                            "id": ident,
                            "title": title,
                            "page": pno,
                            "section_id": None,
                        }
                    )
        return results
