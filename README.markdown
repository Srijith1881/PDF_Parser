# USB Power Delivery Specification Parser 🚀

## 📋 Table of Contents
- [Introduction](#introduction)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [OOP Design](#oop-design)
- [Testing](#testing)
- [Frontend Repo](#frontend-repo)
- [Thank You](#thank-you)

## Introduction
Navigating massive technical documents like the USB Power Delivery (USB PD) specification—often spanning 1000+ pages—can be a daunting task for engineers, technical writers, and documentation teams. These PDFs are packed with complex hierarchies, nested sections, tables, figures, and unstructured text, making it challenging to extract actionable insights or integrate with modern systems. 📄

The **USB PD Specification Parsing and Structuring System** solves this problem by transforming raw USB PD specification PDFs into structured, machine-readable formats. This tool automatically extracts the Table of Contents (TOC), sections, subsections, and metadata (like tables and figures), outputting them as JSONL files and generating a validation report in Excel. With a FastAPI backend and an integrated React frontend, it empowers users to search, analyze, and integrate USB PD data with ease. ⚡

## Key Features
- **Automated TOC Detection**: Dynamically identifies TOC page ranges (e.g., pages 13–34), excluding irrelevant sections like "Revision History."
- **Hierarchical Parsing**: Accurately extracts nested TOC entries (e.g., `2`, `2.1`, `2.1.1`) with parent-child relationships.
- **Full Section Extraction**: Pulls complete section content based on TOC page ranges, preserving logical structure.
- **Metadata Extraction**: Identifies and tags tables and figures with their IDs, titles, and page numbers.
- **AI-Enhanced Cleanup**: Optional AI helpers (`ai_helpers.py`) for intelligent text cleanup and auto-tagging of sections (e.g., "contracts," "negotiation").
- **Structured Outputs**: Generates JSONL files (`usb_pd_toc.jsonl`, `usb_pd_spec.jsonl`, `usb_pd_metadata.jsonl`) for easy ingestion into vector stores or LLM-based agents.
- **Validation Reports**: Produces a downloadable Excel report (`validation_report.xlsx`) comparing TOC vs. parsed sections and metadata counts.
- **React Dashboard**: Integrated frontend to visualize TOC hierarchy, section counts, missing entries, and download generated files.
- **OOP Refactoring**: Modular, class-based pipeline for extensibility and maintainability.
- **Unit Tests**: Pytest-based test suite to validate pipeline components.

## Architecture
```
[USB PD PDF] --> [FastAPI Backend] --> [JSONL Files + Excel Report]
                                |
                          [React Frontend]
```

### Backend (FastAPI + OOP)
- **`pipeline.py`**: Orchestrates the parsing pipeline using the `Pipeline` class.
- **`pdf_document.py`**: `PDFDocument` class for PDF loading and text extraction.
- **`toc_extractor.py`**: `ToCExtractor` class for TOC parsing and hierarchy detection.
- **`section_extractor.py`**: `SectionExtractor` class for pulling section text.
- **`metadata_extractor.py`**: `MetadataExtractor` class for detecting tables/figures.
- **`validator.py`**: `Validator` class for consistency checks and Excel reports.
- **`utils.py`**: Helper functions for writing JSONL, etc.
- **Workflow**:
  1. The FastAPI server accepts a PDF upload or uses a hardcoded path.
  2. The `Pipeline` class coordinates `PDFDocument`, `ToCExtractor`, `SectionExtractor`, and `MetadataExtractor` to process the PDF.
  3. The `Validator` class ensures consistency and generates reports.
  4. Outputs are saved as JSONL files and an Excel report.

### Frontend (React + Vite)
- **Components**:
  - PDF upload with TOC page range input.
  - Dashboard displaying TOC hierarchy, section counts, metadata counts, and validation summary.
  - Download buttons for JSONL files and Excel report.
- **Interaction**: Communicates with the FastAPI backend via RESTful endpoints to upload PDFs, fetch parsed data, and download files.

## Quick Start
Get up and running in minutes! 🚀

### Prerequisites
- Python 3.8+
- Node.js (for React frontend)
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
4. Run the FastAPI server:
   ```bash
   uvicorn server:app --reload
   ```
   Access the API at `http://localhost:8000/docs`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React app:
   ```bash
   npm run dev
   ```
   Access the dashboard at `http://localhost:3000`.

## API Endpoints
The FastAPI backend provides the following endpoints:

- **`POST /parse`**
  - **Description**: Upload a PDF and run the parsing pipeline.
  - **Body**: `{ "file": <binary>, "toc_start_page": <int>, "toc_end_page": <int> }` (multipart form-data).
  - **Response**: `{ "status": "success", "job_id": "<uuid>", "message": "Processing started" }`

- **`GET /jobs/{job_id}`**
  - **Description**: Fetch job status and file paths.
  - **Response**: `{ "job_id": "<uuid>", "status": "completed/processing/failed", "files": { "toc": "<path>", "sections": "<path>", "metadata": "<path>", "report": "<path>" } }`

- **`GET /download/{job_id}/{filename}`**
  - **Description**: Download generated files (`toc`, `sections`, `metadata`, `report`).
  - **Parameters**: `filename` = `toc`, `sections`, `metadata`, or `report`.
  - **Response**: Binary file (e.g., `usb_pd_toc.jsonl`).

- **`GET /health`**
  - **Description**: Health check for the API.
  - **Response**: `{ "status": "healthy" }`

Access the API documentation at `http://localhost:8000/docs` when the server is running.

## OOP Design
The project uses an object-oriented design for modularity and maintainability:

- **`PDFDocument`**: Encapsulates PDF loading and text extraction using PyMuPDF.
- **`ToCExtractor`**: Handles TOC detection, parsing, and range resolution with regex.
- **`SectionExtractor`**: Extracts sections/subsections based on TOC hierarchy.
- **`MetadataExtractor`**: Collects metadata (tables/figures) with regex-based detection.
- **`Validator`**: Ensures consistency across TOC, sections, and metadata; generates Excel reports.
- **`Pipeline`**: High-level orchestrator, coordinating all extractors and validators.

### Benefits
- **Separation of Concerns**: Each class handles a specific task, improving code clarity.
- **Testability**: Individual classes can be unit-tested independently.
- **Extensibility**: Easily adaptable for other technical specifications.
- **Maintainability**: Reduced cyclomatic complexity and clear interfaces.

## Testing
The project includes a Pytest-based test suite to validate functionality.

### Run Tests
```bash
pytest -v
```

### Example Tests
- ✅ `test_pdf_document.py`: Verifies correct page count and text extraction.
- ✅ `test_toc_extractor.py`: Validates TOC parsing and hierarchy construction.
- ✅ `test_section_extractor.py`: Ensures sections align with TOC page ranges.
- ✅ `test_metadata_extractor.py`: Confirms accurate detection of tables and figures.
- ✅ `test_validator.py`: Verifies validation report generation and consistency checks.

Adding tests ensures robustness, catches regressions, and improves maintainability.

## Frontend Repo
The React frontend is included in the same repository under the `/frontend` directory for simplicity. Explore it at `usb-pd-parser/frontend`.

## Thank You
Thank you for exploring the USB PD Specification Parser! 🎉 We built this tool to make complex technical documents more accessible and actionable. With its OOP design, comprehensive unit tests, and modular architecture, it’s crafted for engineers, researchers, and documentation teams to save time and improve accuracy. 🙏 Contributions, issues, and feedback are always welcome on GitHub! 🚀