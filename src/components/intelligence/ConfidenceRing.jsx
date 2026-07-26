import React from 'react';

export default function ConfidenceRing({ score, level }) {
  const radius = 35;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="confidence-ring-wrapper">
      <svg className="confidence-ring-svg" width="90" height="90">
        <circle 
          className="confidence-ring-bg" 
          cx="45" 
          cy="45" 
          r={radius} 
        />
        <circle 
          className="confidence-ring-fill" 
          cx="45" 
          cy="45" 
          r={radius} 
          style={{
            strokeDasharray: circumference,
            strokeDashoffset: strokeDashoffset
          }}
        />
        <text className="confidence-ring-text" x="50%" y="50%" dy="4">
          {score}%
        </text>
      </svg>
      <div className="confidence-level-label">
        <span className="confidence-kicker">Certainty</span>
        <strong className="confidence-level-val">{level}</strong>
      </div>
    </div>
  );
}
