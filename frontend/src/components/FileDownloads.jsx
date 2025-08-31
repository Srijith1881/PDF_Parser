import React from "react";

function FileDownloads({ jobId, files }) {
  if (!files) return null;

  return (
    <div className="downloads">
      <h2>📂 Download Files</h2>
      <ul>
        {Object.entries(files).map(([key, path]) => {
          const filename = path.split("/").pop();
          return (
            <li key={key}>
              <a
                href={`http://localhost:8000/download/${jobId}/${filename}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                ⬇️ {filename}
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default FileDownloads;
