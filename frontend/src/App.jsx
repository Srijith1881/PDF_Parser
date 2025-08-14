import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import KPICards from "./components/KPICards";
import FileDownloads from "./components/FileDownloads";
import "./index.css";

function App() {
  const [jobData, setJobData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (formData) => {
    setLoading(true);
    setError("");
    setJobData(null);

    try {
      const res = await fetch("http://localhost:8000/parse", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
      }

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
      <UploadForm onUpload={handleUpload} loading={loading} />
      {error && <p className="error">{error}</p>}

      {loading && <p>Processing... please wait</p>}

      {jobData && (
        <>
          <KPICards counts={jobData.counts} />
          <FileDownloads jobId={jobData.job_id} files={jobData.files} />
        </>
      )}
    </div>
  );
}

export default App;
