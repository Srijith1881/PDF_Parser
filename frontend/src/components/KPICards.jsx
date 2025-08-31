import React from "react";

function KPICards({ counts }) {
  if (!counts) return null;

  return (
    <div className="kpi-cards">
      <div className="card">
        <h3>📑 ToC Entries</h3>
        <p>{counts.toc || 0}</p>
      </div>
      <div className="card">
        <h3>📄 Sections</h3>
        <p>{counts.sections || 0}</p>
      </div>
      <div className="card">
        <h3>📊 Metadata</h3>
        <p>{counts.metadata || 0}</p>
      </div>
      <div className="card">
        <h3>✅ Validations</h3>
        <p>{counts.validations || 0}</p>
      </div>
    </div>
  );
}

export default KPICards;
