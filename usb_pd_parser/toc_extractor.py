from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .config import Config
from .pdf_document import PDFDocument
from .utils import split_lines


@dataclass
class ToCExtractor:
    cfg: Config

    # ---------- public API ----------
    def extract(
        self,
        pdf: PDFDocument,
        doc_title: str,
        toc_start: Optional[int] = None,
        toc_end: Optional[int] = None,
    ) -> List[Dict]:
        start, end = self._resolve_toc_range(pdf, toc_start, toc_end)
        page_texts = pdf.load_pages_text(range(start, end + 1))
        lines = self._collect_toc_lines(page_texts, start)
        # core parse
        entries = self._parse_lines(lines, doc_title)
        # parent preservation (ensure 2, 2.1 exist if 2.1.1 present)
        entries = self._ensure_parent_sections(entries, doc_title)
        # sort by numeric id
        entries.sort(key=self._section_sort_key)
        return entries

    # ---------- range detection ----------
    def _resolve_toc_range(
        self, pdf: PDFDocument, start: Optional[int], end: Optional[int]
    ) -> Tuple[int, int]:
        start = start or self.cfg.toc_start_hint
        end = end or self.cfg.toc_end_hint
        total = pdf.num_pages()

        if start and end:
            return max(1, start), min(end, total)

        # auto-detect
        auto = self._detect_toc_range(pdf)
        if auto:
            return auto

        # fallback
        fallback_end = min(self.cfg.toc_default_pages, total)
        return 1, fallback_end

    def _detect_toc_range(self, pdf: PDFDocument) -> Optional[Tuple[int, int]]:
        texts = pdf.load_pages_text(range(1, min(self.cfg.max_scan_pages, pdf.num_pages()) + 1))

        def has_heading(text: str, phrases: Sequence[str]) -> bool:
            low = (text or "").lower()
            return any(p in low for p in phrases)

        def tocish_count(text: str) -> int:
            pat = re.compile(r"^\s*\d+(?:\.\d+)*\s+\S+")
            return sum(1 for l in split_lines(text) if pat.match(l))

        start: Optional[int] = None
        # 1) look for explicit heading
        for i, t in enumerate(texts, start=1):
            if has_heading(t, self.cfg.toc_heading_keywords):
                start = i
                break

        # 2) if not found: dense numeric lines
        if start is None:
            dense = [(i + 1, tocish_count(t)) for i, t in enumerate(texts)]
            candidates = [p for p, c in dense if c >= 6]
            if candidates:
                start = min(candidates)
                end = start
                p = start + 1
                while p <= len(texts) and tocish_count(texts[p - 1]) >= 3:
                    end = p
                    p += 1
                return start, end

        # 3) if found heading, seek end
        if start is not None:
            end = start
            for p in range(start, len(texts) + 1):
                t = texts[p - 1] or ""
                if tocish_count(t) <= 2 and re.search(r"^\s*1(\.\d+)*\s", t, re.M):
                    end = p
                    break
                end = p
            return start, end

        return None

    # ---------- line collection & parsing ----------
    def _collect_toc_lines(self, page_texts: List[str], start_page_num: int) -> List[str]:
        lines: List[str] = []
        for page_offset, text in enumerate(page_texts):
            pno = start_page_num + page_offset
            low = (text or "").lower()
            if any(key in low for key in self.cfg.toc_exclude_page_headings):
                # skip revision/errata pages inside the range
                continue
            lines.extend(split_lines(text))
        # join wrapped titles
        return self._join_wrapped(lines)

    def _join_wrapped(self, lines: List[str]) -> List[str]:
        out: List[str] = []
        sec_start = re.compile(r"^\s*\d+(?:\.\d+)*\s+")
        for line in lines:
            if not out:
                out.append(line)
                continue
            if sec_start.match(line):
                out.append(line)
            else:
                out[-1] = (out[-1].rstrip() + " " + line.strip()).strip()
        return out

    def _parse_lines(self, lines: List[str], doc_title: str) -> List[Dict]:
        # Three tolerant patterns: dotted leaders, trailing page number, no page
        pat_dotted = re.compile(self.cfg.toc_regex)
        pat_endnum = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)\s*$")
        pat_nopage = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*$")

        items: List[Dict] = []
        for raw in lines:
            sec_id: Optional[str] = None
            title: Optional[str] = None
            page: Optional[int] = None

            m = pat_dotted.match(raw)
            if m:
                sec_id, title, page = m.group(1).strip(), m.group(3).strip().rstrip("."), int(m.group(4))
            else:
                m = pat_endnum.match(raw)
                if m:
                    sec_id, title, page = m.group(1).strip(), m.group(2).strip().rstrip("."), int(m.group(3))
                else:
                    m = pat_nopage.match(raw)
                    if m:
                        sec_id, title = m.group(1).strip(), m.group(2).strip().rstrip(".")

            if not sec_id or not title:
                continue

            level = sec_id.count(".") + 1
            parent = sec_id.rsplit(".", 1)[0] if level > 1 else None
            items.append(
                {
                    "doc_title": doc_title,
                    "section_id": sec_id,
                    "title": title,
                    "full_path": f"{sec_id} {title}",
                    "page": int(page) if page else 1,
                    "level": level,
                    "parent_id": parent,
                    "tags": [],
                }
            )
        return items

    # ---------- hierarchy helpers ----------
    def _ensure_parent_sections(self, items: List[Dict], doc_title: str) -> List[Dict]:
        """If 2.1.1 exists but 2 or 2.1 missing, synthesize parents."""
        by_id = {i["section_id"]: i for i in items}
        needed: List[str] = []
        for sec in list(by_id):
            parts = sec.split(".")
            for k in range(1, len(parts)):
                parent_id = ".".join(parts[:k])
                if parent_id not in by_id:
                    needed.append(parent_id)

        # de-duplicate and sort by depth (create shallow parents first)
        needed = sorted(set(needed), key=lambda s: (s.count("."), tuple(int(x) for x in s.split("."))))
        for pid in needed:
            level = pid.count(".") + 1
            parent = pid.rsplit(".", 1)[0] if level > 1 else None
            by_id[pid] = {
                "doc_title": doc_title,
                "section_id": pid,
                "title": f"Section {pid}",
                "full_path": f"{pid} Section {pid}",
                "page": 1,
                "level": level,
                "parent_id": parent,
                "tags": [],
            }
        return list(by_id.values())

    @staticmethod
    def _section_sort_key(e: Dict) -> Tuple[int, ...]:
        try:
            return tuple(int(p) for p in e["section_id"].split("."))
        except Exception:
            return (10**9,)
