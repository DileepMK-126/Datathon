import React from 'react';

export default function BriefSummary({ summary }) {
  return (
    <div className="brief-summary-container">
      <h3 className="brief-summary-title">Command Intelligence Narrative</h3>
      <p className="brief-summary-text">"{summary}"</p>
    </div>
  );
}
