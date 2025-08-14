
# app.py
import streamlit as st
import pandas as pd
import os
import tempfile
import subprocess
import json

from config import Config

st.set_page_config(page_title="USB PD Parser", layout="wide")
st.title("USB Power Delivery (USB-PD) – PDF Parser")

with st.sidebar:
    st.header("Run Parser")
    doc_title = st.text_input("Document Title", "USB Power Delivery Specification")
    toc_start = st.number_input("ToC Start Page (optional)", min_value=1, value=13)
    toc_end = st.number_input("ToC End Page (optional)", min_value=1, value=34)
    use_manual_range = st.checkbox("Use manual ToC range", value=True)

    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    run_btn = st.button("Run")

cfg = Config()
out_dir = "."

def _read_jsonl(path):
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().splitlines() if line.strip()]

if run_btn and uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
        tf.write(uploaded.read())
        pdf_path = tf.name

    # Build command
    cmd = ["python", "main.py", "--pdf", pdf_path, "--doc_title", doc_title]
    if use_manual_range and toc_start and toc_end:
        cmd += ["--toc_start", str(int(toc_start)), "--toc_end", str(int(toc_end))]

    with st.spinner("Running the parser..."):
        # Call the pipeline
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            st.error(f"Parsing failed:\n{proc.stderr}\n{proc.stdout}")
        else:
            st.success("Parsing finished.")

# Show outputs if present
toc_items = _read_jsonl(cfg.toc_jsonl)
sec_items = _read_jsonl(cfg.sections_jsonl)
meta_items = _read_jsonl(cfg.metadata_jsonl)

col1, col2, col3, col4 = st.columns(4)
col1.metric("ToC entries", len(toc_items))
col2.metric("Sections parsed", len(sec_items))
col3.metric("Metadata found", len(meta_items))
col4.metric("Output dir", os.path.abspath(out_dir))

# Preview tables
st.subheader("ToC Preview")
if toc_items:
    st.dataframe(pd.DataFrame(toc_items).head(50), use_container_width=True)
else:
    st.info("No ToC parsed yet.")

st.subheader("Sections Preview")
if sec_items:
    st.dataframe(pd.DataFrame([{k:v for k,v in d.items() if k != "text"} for d in sec_items]).head(50), use_container_width=True)
else:
    st.info("No sections yet.")

st.subheader("Metadata (tables/figures)")
if meta_items:
    st.dataframe(pd.DataFrame(meta_items).head(50), use_container_width=True)
else:
    st.info("No metadata found.")

# Downloads
st.subheader("Downloads")
for label, path in [
    ("ToC JSONL", cfg.toc_jsonl),
    ("Sections JSONL", cfg.sections_jsonl),
    ("Metadata JSONL", cfg.metadata_jsonl),
    ("Validation Excel", cfg.validation_report),
]:
    if os.path.exists(path):
        with open(path, "rb") as f:
            st.download_button(label=f"Download {label}", data=f, file_name=os.path.basename(path), mime="application/octet-stream")
    else:
        st.write(f"Missing: {path}")
