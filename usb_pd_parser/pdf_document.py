from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional
import pdfplumber


@dataclass
class PDFDocument:
    path: str
    _all_text: Optional[List[str]] = None   # cache

    def num_pages(self) -> int:
        with pdfplumber.open(self.path) as pdf:
            return len(pdf.pages)

    def load_all_text(self) -> List[str]:
        """Load text for all pages; cached after first call. Pages are 1-indexed externally."""
        if self._all_text is None:
            with pdfplumber.open(self.path) as pdf:
                self._all_text = [(p.extract_text() or "") for p in pdf.pages]
        return self._all_text

    def load_pages_text(self, pages: Optional[Iterable[int]] = None) -> List[str]:
        """Load text for specific 1-indexed page numbers."""
        all_text = self.load_all_text()
        if pages is None:
            return all_text
        out: List[str] = []
        for p in pages:
            if 1 <= p <= len(all_text):
                out.append(all_text[p - 1])
        return out
