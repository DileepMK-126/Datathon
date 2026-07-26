import React from 'react';
import { Target, CheckCircle2 } from 'lucide-react';

export default function IntelligenceHighlights({ highlights }) {
  if (!highlights || highlights.length === 0) return null;

  return (
    <div className="brief-highlights-container">
      <h3 className="brief-highlights-title">Key Intelligence Highlights</h3>
      <ul className="brief-highlights-list">
        {highlights.map((item, idx) => (
          <li key={idx} className="brief-highlight-item">
            <CheckCircle2 size={14} className="text-orange" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
