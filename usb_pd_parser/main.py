from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import Config
from .pipeline import Pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("usb_pd_parser")


def main() -> None:
    parser = argparse.ArgumentParser(description="USB-PD PDF parser (OO)")
    parser.add_argument("--pdf", required=True, help="Path to USB PD PDF")
    parser.add_argument("--doc_title", required=True, help="Document title")
    parser.add_argument("--out_dir", default=".", help="Output directory")
    parser.add_argument("--toc_start", type=int, default=None, help="ToC start page")
    parser.add_argument("--toc_end", type=int, default=None, help="ToC end page")
    args = parser.parse_args()

    if not Path(args.pdf).exists():
        logger.error("PDF not found: %s", args.pdf)
        raise SystemExit(2)

    cfg = Config()
    outputs = Pipeline(cfg).run(
        pdf_path=args.pdf,
        doc_title=args.doc_title,
        out_dir=args.out_dir,
        toc_start=args.toc_start,
        toc_end=args.toc_end,
    )
    logger.info("Done. Outputs:\n%s", "\n".join(f"{k}: {v}" for k, v in outputs.items()))


if __name__ == "__main__":
    main()
