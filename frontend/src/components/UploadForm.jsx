import React, { useState } from "react";

function UploadForm({ onUpload, loading }) {
  const [file, setFile] = useState(null);
  const [docTitle, setDocTitle] = useState("USB Power Delivery Specification");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a PDF file");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_title", docTitle);

    onUpload(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
        disabled={loading}
      />
      <input
        type="text"
        value={docTitle}
        onChange={(e) => setDocTitle(e.target.value)}
        placeholder="Document Title"
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Uploading..." : "Upload & Parse"}
      </button>
    </form>
  );
}

export default UploadForm;
