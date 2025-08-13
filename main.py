# main.py
import argparse
from extract_toc import extract_toc_from_pdf
from extract_sections import extract_sections_from_pdf, extract_metadata_from_sections
from utils import write_jsonl
from config import Config
from validate import validate_toc_vs_sections, generate_excel_report
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Hardcoded PDF path
    # pdf_path = "./USB_PD_Specification.pdf"
    pdf_path = "./USB_PD.pdf"
    doc_title = "USB Power Delivery Specification"
    toc_pages = None  # Or set a fixed number like 10
    out_dir = "."

    if not os.path.exists(pdf_path):
        logger.error("PDF not found: %s", pdf_path)
        sys.exit(2)

    cfg = Config()
    logger.info("Extracting ToC from first %s pages...", toc_pages or cfg.toc_default_pages)
    toc = extract_toc_from_pdf(pdf_path, doc_title, toc_pages=toc_pages)

    toc_out = os.path.join(out_dir, cfg.toc_jsonl)
    write_jsonl(toc, toc_out)

    logger.info("Extracting sections based on ToC page ranges...")
    sections = extract_sections_from_pdf(pdf_path, toc, doc_title)
    sections_out = os.path.join(out_dir, cfg.sections_jsonl)
    write_jsonl(sections, sections_out)

    logger.info("Extracting metadata (tables/figures) heuristically...")
    metadata = extract_metadata_from_sections(sections, doc_title)
    metadata_out = os.path.join(out_dir, cfg.metadata_jsonl)
    write_jsonl(metadata, metadata_out)

    logger.info("Validating ToC vs Sections...")
    validation_results = validate_toc_vs_sections(toc, sections, metadata)
    report_out = os.path.join(out_dir, cfg.validation_report)
    generate_excel_report(validation_results, report_out)

    logger.info("All done. Outputs written to: %s", os.path.abspath(out_dir))
    logger.info("Files: %s, %s, %s, %s", toc_out, sections_out, metadata_out, report_out)

if __name__ == "__main__":
    main()
