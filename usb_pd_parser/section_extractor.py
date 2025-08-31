from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .pdf_document import PDFDocument
from .utils import normalize_ws


@dataclass
class SectionExtractor:
    def extract(self, pdf: PDFDocument, toc: List[Dict]) -> List[Dict]:
        """Slice section text by page ranges derived from ToC ordering."""
        if not toc:
            return []

        # Sort by section index to compute page ranges
        toc_sorted = sorted(toc, key=lambda e: tuple(int(x) for x in e["section_id"].split(".")))
        # derive start page per entry; next entry's start - 1 as end
        spans: List[Tuple[int, int]] = []
        for i, entry in enumerate(toc_sorted):
            start = max(1, int(entry.get("page", 1)))
            if i < len(toc_sorted) - 1:
                next_start = max(1, int(toc_sorted[i + 1].get("page", start)))
                end = max(start, next_start - 1)
            else:
                end = pdf.num_pages()
            spans.append((start, end))

        all_pages = pdf.load_all_text()
        sections: List[Dict] = []
        for entry, (start, end) in zip(toc_sorted, spans):
            joined = " ".join(normalize_ws(all_pages[p - 1]) for p in range(start, min(end, len(all_pages)) + 1))
            item = {
                **entry,
                "text": joined.strip(),
            }
            sections.append(item)
        return sections
