# extract_sections.py  (only tiny improvements)
from typing import List, Dict
from utils import load_pdf_text
from config import Config
import re
import logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_sections_from_pdf(pdf_path: str, toc_data: List[Dict], doc_title: str) -> List[Dict]:
    if not toc_data:
        return []

    toc_sorted = sorted(toc_data, key=lambda x: (x['page'], tuple(int(p) for p in x['section_id'].split('.'))))

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

    sections = []
    for idx, entry in enumerate(toc_sorted):
        start_page = int(entry['page'])
        if idx + 1 < len(toc_sorted):
            next_page = int(toc_sorted[idx + 1]['page'])
            end_page = max(start_page, next_page - 1)
        else:
            end_page = total_pages

        start_page = max(1, min(start_page, total_pages))
        end_page = max(1, min(end_page, total_pages))

        page_nums = list(range(start_page, end_page + 1))
        texts = load_pdf_text(pdf_path, pages=page_nums)
        text_joined = "\n\n".join([f"----- Page {p} -----\n{t or ''}" for p, t in zip(page_nums, texts)])

        sections.append({
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
        })

    logger.info("Extracted %d sections (pages up to %d)", len(sections), total_pages)
    return sections
def extract_metadata_from_sections(sections: list[dict], doc_title: str) -> list[dict]:
    """
    Extracts metadata (tables/figures) from parsed sections.
    Returns a list of dicts matching the metadata schema.
    """
    cfg = Config()
    metadata = []
    for section in sections:
        text = section.get("content", "")
        page = section.get("page")
        for mtype, pattern in cfg.metadata_regexes.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                metadata.append({
                    "doc_title": doc_title,
                    "type": mtype,
                    "id": match,
                    "title": match,
                    "page": page
                })
    return metadata