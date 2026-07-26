import React from 'react';
import { Download, FileJson } from 'lucide-react';

export default function SummaryCard({ summary, onExportJson, onExportPdf, userRole }) {
  const isSupervisorOrAdmin = userRole === 'supervisor' || userRole === 'admin';

  const handleExportPdf = () => {
    if (!isSupervisorOrAdmin) {
      alert("Permission denied. Only Supervisors and Administrators can export reports.");
      return;
    }
    onExportPdf();
  };

  const handleExportJson = () => {
    if (!isSupervisorOrAdmin) {
      alert("Permission denied. Only Supervisors and Administrators can export reports.");
      return;
    }
    onExportJson();
  };

  return (
    <div className="explanation-summary-card">
      <p className="summary-text">"{summary}"</p>
      
      <div className="explanation-export-buttons">
        <button 
          className="btn btn-secondary btn-sm"
          onClick={handleExportJson}
          title="Export Explanation as JSON"
        >
          <FileJson size={13} />
          <span>Export JSON</span>
        </button>
        <button 
          className="btn btn-primary btn-sm"
          onClick={handleExportPdf}
          title="Export PDF Brief"
        >
          <Download size={13} />
          <span>Export PDF</span>
        </button>
      </div>
    </div>
  );
}
