import React from 'react';

export default function ProgressBar({ currentStep, totalSteps }) {
  const percentage = Math.round((currentStep / (totalSteps - 1)) * 100);

  return (
    <div className="demo-progress-bar-wrapper">
      <div className="demo-progress-text-row">
        <span>Step Progress</span>
        <span>{percentage}% Complete</span>
      </div>
      <div className="demo-progress-track">
        <div 
          className="demo-progress-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
