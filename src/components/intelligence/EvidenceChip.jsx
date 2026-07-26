import React from 'react';
import { Link2 } from 'lucide-react';

export default function EvidenceChip({ evidence }) {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="evidence-trace-section">
      <div className="evidence-trace-label">Evidence Traces:</div>
      <div className="evidence-chips-container">
        {evidence.map(item => (
          <a 
            key={item.id} 
            href={item.link} 
            className="evidence-chip-item"
            target="_blank" 
            rel="noopener noreferrer"
            onClick={e => {
              // We prevent default if we want custom modal detail loading, or simply link out
              e.preventDefault();
              alert(`Traced Evidence Detail:\nType: ${item.type}\nID: ${item.id}\nInfo: ${item.description}`);
            }}
          >
            <Link2 size={12} />
            <span>{item.case_id ?? item.id}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
