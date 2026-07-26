import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, CheckCircle2 } from 'lucide-react';

export default function EvidenceAccordion({ evidence, relatedCases }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="evidence-accordion-container">
      <button 
        type="button"
        className="evidence-accordion-header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>Supporting Evidence Traces ({evidence.length})</span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isOpen && (
        <div className="evidence-accordion-body">
          <ul className="evidence-bullets-list">
            {evidence.map((item, idx) => (
              <li key={idx} className="evidence-bullet-item">
                <CheckCircle2 size={12} className="text-green" />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          {relatedCases && relatedCases.length > 0 && (
            <div className="evidence-cases-section">
              <span className="evidence-cases-label">Related Case Profiles:</span>
              <div className="evidence-cases-badges">
                {relatedCases.map(caseId => (
                  <span key={caseId} className="evidence-case-badge">
                    <FileText size={10} />
                    <span>{caseId}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
