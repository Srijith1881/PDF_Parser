import React from "react";

function FileDownloads({ jobId, files }) {
  const backendBase = "http://localhost:8000";

  const downloadables = [
    { name: "ToC JSONL", file: "usb_pd_toc.jsonl" },
    { name: "Sections JSONL", file: "usb_pd_spec.jsonl" },
    { name: "Metadata JSONL", file: "usb_pd_metadata.jsonl" },
    { name: "Validation Report (Excel)", file: "validation_report.xlsx" },
  ];

  return (
    <div className="downloads">
      <h2>Download Outputs</h2>
      {downloadables.map((d) => (
        <a
          key={d.file}
          href={`${backendBase}/download/${jobId}/${d.file}`}
          target="_blank"
          rel="noopener noreferrer"
          className="download-btn"
        >
          {d.name}
        </a>
      ))}
    </div>
  );
}

export default FileDownloads;
