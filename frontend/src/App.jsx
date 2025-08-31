import React, { useState } from "react";
import "./index.css";

function App() {
  const [jobData, setJobData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    setLoading(true);
    setError("");
    setJobData(null);

    try {
      const res = await fetch("http://localhost:8000/parse", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Error: ${res.status} ${res.statusText}`);

      const data = await res.json();
      setJobData(data);
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>USB PD Specification Parser</h1>
      <form onSubmit={handleUpload}>
        <input type="file" name="file" accept="application/pdf" required />
        <input type="number" name="toc_start" placeholder="ToC Start Page" />
        <input type="number" name="toc_end" placeholder="ToC End Page" />
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Upload & Parse"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {jobData && (
        <>
          <h2>📊 Results</h2>
          <ul>
            <li>📑 ToC Entries: {jobData.counts.toc}</li>
            <li>📄 Sections: {jobData.counts.sections}</li>
            <li>📊 Metadata: {jobData.counts.metadata}</li>
            <li>✅ Validations: {jobData.counts.validation}</li>
          </ul>

          <h3>📂 Downloads</h3>
          <ul>
            <li><a href={`http://localhost:8000${jobData.files.toc_jsonl}`} download>Download ToC JSONL</a></li>
            <li><a href={`http://localhost:8000${jobData.files.sections_jsonl}`} download>Download Sections JSONL</a></li>
            <li><a href={`http://localhost:8000${jobData.files.metadata_jsonl}`} download>Download Metadata JSONL</a></li>
            <li><a href={`http://localhost:8000${jobData.files.validation_xlsx}`} download>Download Validation Report</a></li>
          </ul>
        </>
      )}
    </div>
  );
}

export default App;
