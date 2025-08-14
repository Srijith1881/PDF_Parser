import React from "react";

function KPICards({ counts }) {
  const items = [
    { label: "ToC Entries", value: counts.toc },
    { label: "Sections", value: counts.sections },
    { label: "Metadata Items", value: counts.metadata },
    { label: "Missing Sections", value: counts.missing_sections },
    { label: "Extra Sections", value: counts.extra_sections },
  ];

  return (
    <div className="kpi-container">
      {items.map((item) => (
        <div key={item.label} className="kpi-card">
          <h3>{item.value}</h3>
          <p>{item.label}</p>
        </div>
      ))}
    </div>
  );
}

export default KPICards;
