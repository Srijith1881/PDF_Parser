import re
from typing import List, Dict, Optional, Tuple
from config import Config
from utils import load_pdf_text
import logging
import pdfplumber

logger = logging.getLogger(__name__)

# ---------- helpers ----------

def _page_has_heading(text: str, phrases: List[str]) -> bool:
    if not text:
        return False
    low = text.lower()
    return any(p in low for p in phrases)

def _count_tocish_lines(text: str) -> int:
    if not text:
        return 0
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pat = re.compile(r'^\d+(?:\.\d+)*\s+\S+')
    return sum(1 for l in lines if pat.match(l))

def _detect_toc_range(pdf_path: str, cfg: Config, max_scan_pages: int = 80) -> Tuple[Optional[int], Optional[int]]:
    texts = load_pdf_text(pdf_path, pages=list(range(1, max_scan_pages + 1)))

    start = None
    for idx, t in enumerate(texts, start=1):
        if _page_has_heading(t, cfg.toc_heading_keywords):
            start = idx
            break

    if start is None:
        densities = [(i+1, _count_tocish_lines(t)) for i, t in enumerate(texts)]
        candidates = [p for p, c in densities if c >= 6]
        if candidates:
            start = min(candidates)
            end = start
            p = start + 1
            while p <= len(texts) and _count_tocish_lines(texts[p-1]) >= 3:
                end = p
                p += 1
            return start, end

    if start is not None:
        end = start
        for p in range(start, min(len(texts), max_scan_pages)):
            page_text = texts[p-1] or ""
            if _count_tocish_lines(page_text) <= 2 and re.search(r'^\s*1(\.\d+)*\s', page_text, re.M):
                end = p
                break
            end = p
        return start, end

    return None, None

# ---------- improved line joining and cleaning ----------

def _join_wrapped_toc_lines(lines: List[str], cfg: Config) -> List[str]:
    """
    Join continuation lines & remove Figures/Tables from TOC.
    """
    out = []
    sec_start = re.compile(r'^\s*\d+(?:\.\d+)*\s+')
    fig_pat = re.compile(cfg.figure_regex, re.I)
    tbl_pat = re.compile(cfg.table_regex, re.I)

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if fig_pat.search(clean_line) or tbl_pat.search(clean_line):
            # skip figure/table entries entirely
            continue

        if not out:
            out.append(clean_line)
            continue

        if sec_start.match(clean_line):
            out.append(clean_line)
        else:
            out[-1] = (out[-1].rstrip() + " " + clean_line).strip()
    return out

def _find_title_page(title: str, all_pages_text: List[str]) -> Optional[int]:
    if not title or not all_pages_text:
        return None
    tt = title.lower()
    for idx, page_text in enumerate(all_pages_text, start=1):
        if page_text and tt in page_text.lower():
            return idx
    return None

def _parse_toc_lines(lines: List[str], cfg: Config, doc_title: str,
                     all_pages_text: Optional[List[str]] = None) -> List[Dict]:
    pat_dotted = re.compile(cfg.toc_regex)
    pat_endnum = re.compile(r'^\s*(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)\s*$')
    pat_nopage = re.compile(r'^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*$')

    results = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        sec_id = title = None
        page = None

        m = pat_dotted.match(line)
        if m:
            sec_id, title, page = m.group(1).strip(), m.group(3).strip().rstrip('.'), int(m.group(4))
        else:
            m = pat_endnum.match(line)
            if m:
                sec_id, title, page = m.group(1).strip(), m.group(2).strip().rstrip('.'), int(m.group(3))
            else:
                m = pat_nopage.match(line)
                if m:
                    sec_id, title = m.group(1).strip(), m.group(2).strip().rstrip('.')

        if not sec_id or not title:
            continue

        if page is None and all_pages_text is not None:
            guessed = _find_title_page(title, all_pages_text)
            page = guessed or 1

        level = sec_id.count('.') + 1
        parent = sec_id.rsplit('.', 1)[0] if level > 1 else None
        results.append({
            "doc_title": doc_title,
            "section_id": sec_id,
            "title": title,
            "full_path": f"{sec_id} {title}",
            "page": int(page) if page else 1,
            "level": level,
            "parent_id": parent,
            "tags": []
        })

    def key(e):
        try:
            return tuple(int(p) for p in e["section_id"].split('.'))
        except Exception:
            return (e["section_id"],)
    results.sort(key=key)
    return results

# ---------- main entry ----------

def extract_toc_from_pdf(pdf_path: str, doc_title: str,
                         toc_pages: Optional[int] = None,
                         toc_start: Optional[int] = None,
                         toc_end: Optional[int] = None) -> List[Dict]:

    cfg = Config()
    if toc_start is None:
        toc_start = cfg.toc_start_hint
    if toc_end is None:
        toc_end = cfg.toc_end_hint

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

    if not toc_start or not toc_end:
        ds, de = _detect_toc_range(pdf_path, cfg, max_scan_pages=min(120, total_pages))
        toc_start = toc_start or ds
        toc_end = toc_end or de

    if not toc_start or not toc_end:
        n = toc_pages or cfg.toc_default_pages
        toc_start, toc_end = 1, min(n, total_pages)
        logger.warning("ToC range not detected; falling back to pages %d-%d", toc_start, toc_end)
    else:
        logger.info("Using ToC range pages %d-%d", toc_start, toc_end)

    raw_texts = load_pdf_text(pdf_path, pages=list(range(toc_start, toc_end + 1)))
    filtered_texts = []
    for pno, txt in zip(range(toc_start, toc_end + 1), raw_texts):
        if _page_has_heading(txt, cfg.toc_exclude_page_headings):
            logger.info("Skipping page %d (looks like Revision/Document History)", pno)
            continue
        filtered_texts.append(txt or "")

    lines = []
    for t in filtered_texts:
        lines.extend([l for l in t.splitlines()])

    lines = _join_wrapped_toc_lines([l for l in lines if l.strip()], cfg)

    all_pages_text = load_pdf_text(pdf_path, pages=None)

    toc_entries = _parse_toc_lines(lines, cfg, doc_title, all_pages_text=all_pages_text)
    logger.info("Parsed %d ToC entries", len(toc_entries))
    return toc_entries
