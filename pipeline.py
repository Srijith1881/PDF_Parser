# pipeline.py
import os
import uuid
import logging
from typing import Optional, Dict, Any

from config import Config
from utils import write_jsonl, load_pdf_text
from extract_toc import extract_toc_from_pdf
from extract_sections import extract_sections_from_pdf, extract_metadata_from_sections
from validate import validate_toc_vs_sections, generate_excel_report

logger = logging.getLogger(__name__)

def run_pipeline(
    pdf_path: str,
    doc_title: str,
    out_dir: Optional[str] = None,
    toc_pages: Optional[int] = None,
    toc_start: Optional[int] = None,
    toc_end: Optional[int] = None,
    use_llm: bool = False,   # reserved for future (ai_helpers)
) -> Dict[str, Any]:
    """
    Orchestrates the full pipeline and returns a summary dict with paths + counts.
    """
    cfg = Config()

    if out_dir is None:
        job_id = str(uuid.uuid4())[:8]
        out_dir = os.path.join("outputs", job_id)
    else:
        job_id = os.path.basename(out_dir)

    os.makedirs(out_dir, exist_ok=True)

    # quick health check on PDF text
    try:
        sample = load_pdf_text(pdf_path, pages=[1])[0]
        logger.info("Page 1 text length: %d", len(sample or ""))
    except Exception as e:
        logger.warning("Failed to read sample page 1: %s", e)

    # 1) ToC
    toc = extract_toc_from_pdf(
        pdf_path=pdf_path,
        doc_title=doc_title,
        toc_pages=toc_pages,
        toc_start=toc_start,
        toc_end=toc_end
    )
    toc_out = os.path.join(out_dir, cfg.toc_jsonl)
    write_jsonl(toc, toc_out)

    # 2) Sections
    sections = extract_sections_from_pdf(pdf_path, toc, doc_title)
    sections_out = os.path.join(out_dir, cfg.sections_jsonl)
    write_jsonl(sections, sections_out)

    # 3) Metadata
    metadata = extract_metadata_from_sections(sections, doc_title)
    metadata_out = os.path.join(out_dir, cfg.metadata_jsonl)
    write_jsonl(metadata, metadata_out)

    # 4) Validation
    validation_results = validate_toc_vs_sections(toc, sections, metadata)
    report_out = os.path.join(out_dir, cfg.validation_report)
    generate_excel_report(validation_results, report_out)

    # Summary
    summary = {
        "job_id": job_id,
        "out_dir": os.path.abspath(out_dir),
        "doc_title": doc_title,
        "counts": {
            "toc": len(toc),
            "sections": len(sections),
            "metadata": len(metadata),
            "missing_sections": len(validation_results.get("missing_sections", [])),
            "extra_sections": len(validation_results.get("extra_sections", [])),
        },
        "files": {
            "toc_jsonl": os.path.abspath(toc_out),
            "sections_jsonl": os.path.abspath(sections_out),
            "metadata_jsonl": os.path.abspath(metadata_out),
            "validation_xlsx": os.path.abspath(report_out),
        },
        "validation": validation_results
    }
    return summary
