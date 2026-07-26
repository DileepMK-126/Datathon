import React from 'react';
import { Volume2, HelpCircle } from 'lucide-react';

export default function DemoStepCard({ stepTitle, narration, directive, stepNumber, totalSteps }) {
  return (
    <div className="demo-step-card-container">
      <div className="demo-step-card-header">
        <span className="demo-step-badge">STEP {stepNumber} of {totalSteps}</span>
        <h3 className="demo-step-title">{stepTitle}</h3>
      </div>

      <div className="demo-narration-section">
        <div className="narration-icon-row">
          <Volume2 size={16} className="text-orange" />
          <span>Presenter Narration Script:</span>
        </div>
        <p className="demo-narration-text">"{narration}"</p>
      </div>

      {directive && (
        <div className="demo-directive-section">
          <HelpCircle size={14} className="text-blue" />
          <span className="demo-directive-text"><strong>Action:</strong> {directive}</span>
        </div>
      )}
    </div>
  );
}
