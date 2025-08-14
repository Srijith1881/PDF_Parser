# main.py
import argparse, os, sys, logging
from pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="USB-PD PDF parser (CLI)")
    parser.add_argument("--pdf", required=True, help="Path to USB PD PDF")
    parser.add_argument("--doc_title", default="USB Power Delivery Specification")
    parser.add_argument("--out_dir", default=None, help="Output directory (if omitted, auto job folder)")
    parser.add_argument("--toc_pages", type=int, default=None)
    parser.add_argument("--toc_start", type=int, default=None)
    parser.add_argument("--toc_end", type=int, default=None)
    parser.add_argument("--use_llm", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        logger.error("PDF not found: %s", args.pdf)
        sys.exit(2)

    result = run_pipeline(
        pdf_path=args.pdf,
        doc_title=args.doc_title,
        out_dir=args.out_dir,
        toc_pages=args.toc_pages,
        toc_start=args.toc_start,
        toc_end=args.toc_end,
        use_llm=args.use_llm
    )

    logger.info("Job %s complete. Outputs in %s", result["job_id"], result["out_dir"])

if __name__ == "__main__":
    main()
