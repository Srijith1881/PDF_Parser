# USB Power Delivery Specification Parser 🚀

## 📋 Table of Contents
1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [API Endpoints](#api-endpoints)
6. [Testing](#testing)
7. [Frontend Repo](#frontend-repo)
8. [Thank You](#thank-you)

## Introduction
Navigating massive technical documents like the USB Power Delivery (USB PD) specification—often spanning 1000+ pages—can be a daunting task for engineers, technical writers, and documentation teams. These PDFs are packed with complex hierarchies, nested sections, tables, figures, and unstructured text, making it challenging to extract actionable insights or integrate with modern systems. 📄

The **USB PD Specification Parsing and Structuring System** solves this problem by transforming raw USB PD specification PDFs into structured, machine-readable formats. This tool automatically extracts the Table of Contents (TOC), sections, subsections, and metadata (like tables and figures), outputting them as JSONL files and generating a validation report in Excel. With a FastAPI backend and an optional React frontend, it empowers users to search, analyze, and integrate USB PD data with ease. Whether you're building documentation pipelines or analyzing protocol details, this system streamlines the process with precision and efficiency. ⚡

## Key Features
- **Automated TOC Detection**: Dynamically identifies TOC page ranges (e.g., pages 13–34), excluding irrelevant sections like "Revision History."
- **Hierarchical Parsing**: Accurately extracts nested TOC entries (e.g., `2`, `2.1`, `2.1.1`) with parent-child relationships.
- **Full Section Extraction**: Pulls complete section content based on TOC page ranges, preserving logical structure.
- **Metadata Extraction**: Identifies and tags tables and figures with their IDs, titles, and page numbers.
- **AI-Enhanced Cleanup**: Optional AI helpers (`ai_helpers.py`) for intelligent text cleanup and auto-tagging of sections (e.g., "contracts," "negotiation").
- **Structured Outputs**: Generates JSONL files (`usb_pd_toc.jsonl`, `usb_pd_spec.jsonl`, `usb_pd_metadata.jsonl`) for easy ingestion into vector stores or LLM-based agents.
- **Validation Reports**: Produces a downloadable Excel report (`validation_report.xlsx`) comparing TOC vs. parsed sections and metadata counts.
- **React Dashboard**: Optional frontend to visualize TOC hierarchy, section counts, missing entries, and download generated files.
- **Modular Design**: Reusable modules (`extract_toc.py`, `extract_sections.py`, `utils.py`, etc.) for extensibility and maintenance.

## Architecture
The system is built with a modular backend and an optional frontend, designed for scalability and ease of integration:

```
[USB PD PDF] --> [FastAPI Backend] --> [JSONL Files + Excel Report]
                                |
                          [React Frontend]
```

### Backend (FastAPI)
- **Components**:
  - `main.py`: CLI entry point and orchestrator for the parsing pipeline.
  - `config.py`: Centralizes configuration (e.g., PDF path, regex patterns, document title).
  - `extract_toc.py`: Parses TOC with dynamic page range detection and hierarchy construction.
  - `extract_sections.py`: Extracts section content using TOC page ranges.
  - `utils.py`: PDF text extraction (via PyMuPDF) and JSONL writing utilities.
  - `validate.py`: Validates parsed data against TOC and generates Excel reports.
  - `schema.py`: Defines JSON schemas for TOC, sections, and metadata.
  - `ai_helpers.py`: Optional LLM-based cleanup and tagging (not included in core pipeline).
- **Workflow**:
  1. The FastAPI server accepts a PDF upload or uses a hardcoded path.
  2. The pipeline extracts TOC, sections, and metadata using regex and PyMuPDF.
  3. Data is validated and written to JSONL files.
  4. An Excel report is generated with validation metrics.

### Frontend (React)
- **Components**:
  - A dashboard displaying the TOC hierarchy as a tree.
  - Metrics for section counts, missing entries, and metadata.
  - Download buttons for JSONL files and the Excel report.
- **Interaction**: The frontend communicates with the FastAPI backend via RESTful endpoints to upload PDFs, retrieve parsed data, and download files.

### Data Flow
1. User uploads a PDF or specifies a path.
2. Backend processes the PDF, generating JSONL files and a validation report.
3. Frontend fetches and displays the parsed data, allowing users to explore and download outputs.

## Quick Start
Get up and running in minutes! 🚀

### Prerequisites
- Python 3.8+
- Node.js (for React frontend, optional)
- USB PD specification PDF (`usb_pd_spec.pdf`)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/usb-pd-parser.git
   cd usb-pd-parser
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Required libraries: `pymupdf`, `pandas`, `openpyxl`, `jsonschema`, `fastapi`, `uvicorn`.
3. Place the PDF at `usb_pd_parser/usb_pd_spec.pdf` or update `PDF_PATH` in `config.py`.
4. Run the CLI pipeline:
   ```bash
   python main.py
   ```
   Outputs: `usb_pd_toc.jsonl`, `usb_pd_spec.jsonl`, `usb_pd_metadata.jsonl`, `validation_report.xlsx`.
5. Alternatively, run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   Access the API at `http://localhost:8000`.

### Frontend Setup (Optional)
1. Frontend is attached with this repo.
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Start the React app:
   ```bash
   npm run dev
   ```
   Access the dashboard at `http://localhost:3000`.

### Streamlit (Optional)
For quick UI testing:
1. Install Streamlit:
   ```bash
   pip install streamlit
   ```
2. Run the Streamlit app (if implemented):
   ```bash
   streamlit run streamlit_app.py
   ```
   Access at `http://localhost:8501`.

## API Endpoints
The FastAPI backend provides the following endpoints:

- **`POST /upload-pdf`**
  - **Description**: Upload a USB PD PDF for parsing.
  - **Body**: `{ "file": <binary> }` (multipart form-data).
  - **Response**: `{ "status": "success", "message": "PDF uploaded and queued for processing" }`

- **`GET /toc`**
  - **Description**: Retrieve the parsed TOC in JSONL format.
  - **Response**: Array of TOC entries (e.g., `{ "section_id": "2.1.2", "title": "Power Delivery Contract Negotiation", ... }`).

- **`GET /sections`**
  - **Description**: Retrieve parsed sections from the PDF body.
  - **Response**: Array of section entries.

- **`GET /metadata`**
  - **Description**: Retrieve parsed metadata (tables and figures).
  - **Response**: Array of metadata entries (e.g., `{ "type": "table", "id": "Table 3-1", ... }`).

- **`GET /validation-report`**
  - **Description**: Download the validation report as an Excel file.
  - **Response**: Binary file (`validation_report.xlsx`).

- **`GET /download/{file_type}`**
  - **Description**: Download generated files (`toc`, `sections`, `metadata`).
  - **Parameters**: `file_type` = `toc`, `sections`, or `metadata`.
  - **Response**: JSONL file (`usb_pd_toc.jsonl`, etc.).

Access the API documentation at `http://localhost:8000/docs` when the server is running.

## Testing
To verify the system's functionality:

1. **CLI Testing**:
   - Run `python main.py` with a sample USB PD PDF.
   - Check output files in the project directory:
     - `usb_pd_toc.jsonl`: Verify TOC hierarchy and page numbers.
     - `usb_pd_spec.jsonl`: Confirm section content and hierarchy.
     - `usb_pd_metadata.jsonl`: Ensure tables and figures are listed.
     - `validation_report.xlsx`: Review metrics for mismatches or missing entries.
   - Example check:
     ```bash
     head usb_pd_toc.jsonl
     ```

2. **API Testing**:
   - Use tools like `curl` or Postman to test endpoints.
   - Example: Upload a PDF:
     ```bash
     curl -X POST -F "file=@usb_pd_spec.pdf" http://localhost:8000/upload-pdf
     ```
   - Example: Fetch TOC:
     ```bash
     curl http://localhost:8000/toc
     ```

3. **Frontend Testing**:
   - Run the React frontend and verify the dashboard displays the TOC hierarchy, metrics, and download links.
   - Ensure download buttons retrieve the correct files.

4. **Validation**:
   - Open `validation_report.xlsx` in Excel to confirm section counts, missing entries, and metadata matches.

## Frontend Repo
The React frontend is attached in the same repository for convenience and accessibility.

## Thank You
Thank you for exploring the USB PD Specification Parser! 🎉 We built this tool to make complex technical documents more accessible and actionable. Whether you're an engineer diving into USB PD protocols or a technical writer streamlining documentation, we hope this system saves you time and effort. Feel free to contribute, raise issues, or reach out with feedback on GitHub. Happy parsing! 😊
