# server.py
import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import run_pipeline

app = FastAPI(title="USB PD Parser API", version="1.0.0")

# CORS for your React app (adjust origins as you like)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in prod
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/parse", response_model=ParseResponse)
async def parse_pdf(
    file: UploadFile = File(...),
    doc_title: str = Form("USB Power Delivery Specification"),
    toc_start: Optional[int] = Form(None),
    toc_end: Optional[int] = Form(None),
    toc_pages: Optional[int] = Form(None),
    use_llm: bool = Form(False)
):
    # Save upload to a temp path
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    os.makedirs("uploads", exist_ok=True)
    upload_path = os.path.join("uploads", file.filename)
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Each job gets its own output dir
    os.makedirs("outputs", exist_ok=True)
    # Pass None for out_dir -> pipeline will create a new job folder
    try:
        result = run_pipeline(
            pdf_path=upload_path,
            doc_title=doc_title,
            out_dir=None,
            toc_pages=toc_pages,
            toc_start=toc_start,
            toc_end=toc_end,
            use_llm=use_llm
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    # Return summary
    return ParseResponse(
        job_id=result["job_id"],
        doc_title=result["doc_title"],
        counts=result["counts"],
        files=result["files"],
        out_dir=result["out_dir"]
    )

@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job_dir = os.path.join("outputs", job_id)
    if not os.path.isdir(job_dir):
        raise HTTPException(status_code=404, detail="Job not found")

    # Basic stats by reading files
    files = {
        "toc_jsonl": os.path.join(job_dir, "usb_pd_toc.jsonl"),
        "sections_jsonl": os.path.join(job_dir, "usb_pd_spec.jsonl"),
        "metadata_jsonl": os.path.join(job_dir, "usb_pd_metadata.jsonl"),
        "validation_xlsx": os.path.join(job_dir, "validation_report.xlsx"),
    }
    return JSONResponse({
        "job_id": job_id,
        "out_dir": os.path.abspath(job_dir),
        "files": {k: os.path.abspath(v) for k, v in files.items()},
    })

@app.get("/download/{job_id}/{filename}")
def download_file(job_id: str, filename: str):
    job_dir = os.path.join("outputs", job_id)
    path = os.path.join(job_dir, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)
