# utils.py
import json
import pdfplumber
from typing import List
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def write_jsonl(data: List[dict], filename: str) -> None:
    """
    Writes a list of dictionaries to a JSONL file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info("Wrote %d records to %s", len(data), filename)


def load_pdf_text(pdf_path: str, pages: list[int] = None) -> list[str]:
    """
    Extracts text from specified pages (1-indexed) using pdfplumber.
    If pages is None, extracts all pages.
    Returns a list of page texts (index 0 corresponds to page 1).
    """
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        if pages is None:
            page_iter = list(range(1, total + 1))
        else:
            page_iter = [p for p in pages if 1 <= p <= total]

        # create a map page_number -> text
        page_texts = {}
        for page_no in page_iter:
            page = pdf.pages[page_no - 1]  # pdfplumber pages are 0-indexed
            try:
                text = page.extract_text() or ""
            except Exception as e:
                logger.warning("Failed to extract text from page %d: %s", page_no, e)
                text = ""
            page_texts[page_no] = text

        # return list for all pages in order. If pages omitted, return full list.
        if pages is None:
            for i in range(1, total + 1):
                texts.append(page_texts.get(i, ""))
        else:
            for p in page_iter:
                texts.append(page_texts.get(p, ""))

    return texts
