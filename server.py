# server.py
import os
import shutil
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from usb_pd_parser.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

app = FastAPI(title="USB PD Parser API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParseResponse(BaseModel):
    job_id: str
    doc_title: str
    counts: dict
    files: dict
    out_dir: str

@app.post("/parse", response_model=ParseResponse)
async def parse_pdf(
    file: UploadFile = File(...),
    doc_title: str = Form("USB Power Delivery Specification"),
    toc_start: Optional[int] = Form(None),
    toc_end: Optional[int] = Form(None),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    os.makedirs("uploads", exist_ok=True)
    upload_path = os.path.join("uploads", f"{uuid.uuid4()}.pdf")
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    os.makedirs("outputs", exist_ok=True)
    job_id = str(uuid.uuid4())
    out_dir = os.path.join("outputs", job_id)

    try:
        result = run_pipeline(
            pdf_path=upload_path,
            doc_title=doc_title,
            out_dir=out_dir,
            toc_start=toc_start,
            toc_end=toc_end,
        )
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    # Count entries
    counts = {
        "toc": sum(1 for _ in open(result["toc"], "r", encoding="utf-8")),
        "sections": sum(1 for _ in open(result["sections"], "r", encoding="utf-8")),
        "metadata": sum(1 for _ in open(result["metadata"], "r", encoding="utf-8")),
        "validation": 1 if os.path.isfile(result["report"]) else 0,
    }

    files = {
        "toc_jsonl": f"/download/{job_id}/{os.path.basename(result['toc'])}",
        "sections_jsonl": f"/download/{job_id}/{os.path.basename(result['sections'])}",
        "metadata_jsonl": f"/download/{job_id}/{os.path.basename(result['metadata'])}",
        "validation_xlsx": f"/download/{job_id}/{os.path.basename(result['report'])}",
    }

    return ParseResponse(
        job_id=job_id,
        doc_title=doc_title,
        counts=counts,
        files=files,
        out_dir=out_dir,
    )

@app.get("/download/{job_id}/{filename}")
def download_file(job_id: str, filename: str):
    job_dir = os.path.join("outputs", job_id)
    path = os.path.join(job_dir, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)
