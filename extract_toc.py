# extract_toc.py
import re
from typing import List, Dict, Optional
from config import Config
from utils import load_pdf_text
import logging

logger = logging.getLogger(__name__)

def _parse_toc_lines(lines: List[str], config: Config, doc_title: str) -> List[Dict]:
    """
    Given lines of text (from ToC pages), returns toc entries.
    Each line is tested against the configured regex.
    """
    pattern = re.compile(config.toc_regex)
    results = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = pattern.match(line)
        if not m:
            # try alternative: numbers at start, title spans until last number (page)
            alt = re.match(r'^(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)$', line)
            if alt:
                sec_id = alt.group(1).strip()
                title = alt.group(2).strip().rstrip('.')
                page = int(alt.group(3))
            else:
                # skip if can't parse
                continue
        else:
            sec_id = m.group(1).strip()
            title = m.group(3).strip().rstrip('.')
            page = int(m.group(4))

        level = sec_id.count('.') + 1
        parent = sec_id.rsplit('.', 1)[0] if level > 1 else None
        entry = {
            "doc_title": doc_title,
            "section_id": sec_id,
            "title": title,
            "full_path": f"{sec_id} {title}",
            "page": page,
            "level": level,
            "parent_id": parent,
            "tags": []
        }
        results.append(entry)

    # sort by numeric section id order (string order can fail)
    def sec_key(e):
        parts = [int(p) for p in e['section_id'].split('.')]
        return parts
    results.sort(key=sec_key)
    logger.info("Parsed %d ToC entries", len(results))
    return results


def extract_toc_from_pdf(pdf_path: str, doc_title: str, toc_pages: Optional[int] = None) -> List[Dict]:
    """
    Reads the first N pages of the PDF, extracts the Table of Contents,
    and returns a list of dicts matching the ToC schema.
    """
    config = Config()
    toc_pages = toc_pages or config.toc_default_pages
    # read 1..toc_pages
    page_nums = list(range(1, toc_pages + 1))
    page_texts = load_pdf_text(pdf_path, pages=page_nums)

    # split into lines and feed into parser
    lines = []
    for t in page_texts:
        if not t:
            continue
        for l in t.splitlines():
            lines.append(l)

    toc_entries = _parse_toc_lines(lines, config, doc_title)
    return toc_entries
