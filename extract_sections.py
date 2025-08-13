# extract_sections.py
from typing import List, Dict
from utils import load_pdf_text
from config import Config
import logging

logger = logging.getLogger(__name__)

def extract_sections_from_pdf(pdf_path: str, toc_data: List[Dict], doc_title: str) -> List[Dict]:
    """
    Reads the full PDF and extracts actual sections based on ToC page ranges.
    Returns structured JSON-ready list of dicts.
    """

    if not toc_data:
        return []

    # Sort toc_data by page number then section id to create ranges
    toc_sorted = sorted(toc_data, key=lambda x: (x['page'], x['section_id']))
    # Build ranges: for each entry, start = page, end = next_entry.page - 1 (or last page)
    # Determine total pages
    # To find last page, read pdf with pdfplumber once to get length
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

    sections = []
    for idx, entry in enumerate(toc_sorted):
        start_page = entry['page']
        if idx + 1 < len(toc_sorted):
            next_page = toc_sorted[idx + 1]['page']
            # If next has same page (nested sections) we still go until next's page -1
            end_page = max(start_page, next_page - 1)
        else:
            end_page = total_pages

        # Clamp
        start_page = max(1, min(start_page, total_pages))
        end_page = max(1, min(end_page, total_pages))

        # Extract text for pages start..end
        page_nums = list(range(start_page, end_page + 1))
        texts = load_pdf_text(pdf_path, pages=page_nums)
        # concatenate — include crude header with page numbers
        text_joined = "\n\n".join([f"----- Page {p} -----\n{t or ''}" for p, t in zip(page_nums, texts)])

        section = {
            "doc_title": doc_title,
            "section_id": entry['section_id'],
            "title": entry['title'],
            "full_path": entry['full_path'],
            "start_page": start_page,
            "end_page": end_page,
            "text": text_joined,
            "level": entry.get('level', entry['section_id'].count('.') + 1),
            "parent_id": entry.get('parent_id'),
            "tags": entry.get('tags', [])
        }
        sections.append(section)

    logger.info("Extracted %d sections (pages up to %d)", len(sections), total_pages)
    return sections


def extract_metadata_from_sections(sections: List[Dict], doc_title: str) -> List[Dict]:
    """
    Scans the combined section texts for metadata entries like tables and figures.
    Returns list of metadata dicts with page hints (attempted).
    Note: this is a heuristic — page detection depends on our text markers '----- Page N -----'
    """
    import re
    from config import Config
    cfg = Config()
    metadata = []
    table_re = re.compile(cfg.table_regex, flags=re.IGNORECASE)
    figure_re = re.compile(cfg.figure_regex, flags=re.IGNORECASE)

    for sec in sections:
        txt = sec['text']
        # find page markers and surrounding lines
        # We attempt to attribute metadata to the first page marker that precedes the match
        # Split into pseudo-pages
        chunks = txt.split("----- Page ")
        for chunk in chunks[1:]:
            # chunk starts like "X -----\n<text...>"
            try:
                first_line, rest = chunk.split("-----\n", 1)
                page_no = int(first_line.strip())
            except Exception:
                continue

            # search for table/figure ids in rest
            for m in table_re.finditer(rest):
                obj_id = m.group(0)
                metadata.append({
                    "doc_title": doc_title,
                    "type": "table",
                    "id": obj_id,
                    "title": None,
                    "page": page_no
                })
            for m in figure_re.finditer(rest):
                obj_id = m.group(0)
                metadata.append({
                    "doc_title": doc_title,
                    "type": "figure",
                    "id": obj_id,
                    "title": None,
                    "page": page_no
                })

    # deduplicate by (type,id,page)
    seen = set()
    unique = []
    for m in metadata:
        key = (m['type'], m['id'], m['page'])
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return unique
