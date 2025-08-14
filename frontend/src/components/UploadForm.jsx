import React, { useState } from "react";

function UploadForm({ onUpload, loading }) {
  const [file, setFile] = useState(null);
  const [docTitle, setDocTitle] = useState("USB Power Delivery Specification");
  const [tocStart, setTocStart] = useState("");
  const [tocEnd, setTocEnd] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a PDF file");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_title", docTitle);
    if (tocStart) formData.append("toc_start", tocStart);
    if (tocEnd) formData.append("toc_end", tocEnd);

    onUpload(formData);
  };

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <label>
        Select PDF:
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </label>

      <label>
        Document Title:
        <input
          type="text"
          value={docTitle}
          onChange={(e) => setDocTitle(e.target.value)}
        />
      </label>

      <label>
        ToC Start Page:
        <input
          type="number"
          value={tocStart}
          onChange={(e) => setTocStart(e.target.value)}
        />
      </label>

      <label>
        ToC End Page:
        <input
          type="number"
          value={tocEnd}
          onChange={(e) => setTocEnd(e.target.value)}
        />
      </label>

      <button type="submit" disabled={loading}>
        {loading ? "Uploading..." : "Upload & Parse"}
      </button>
    </form>
  );
}

export default UploadForm;
