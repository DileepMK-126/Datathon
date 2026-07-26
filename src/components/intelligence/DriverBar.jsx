import React from 'react';

export default function DriverBar({ feature, impact, direction, value }) {
  const isPositive = direction === 'positive';
  const barColor = isPositive ? '#ef5949' : '#10b981'; // Red for Positive risk impact, Green for Negative
  const labelPrefix = isPositive ? '+' : '-';

  return (
    <div className="driver-bar-item">
      <div className="driver-bar-info">
        <span className="driver-name">{feature}</span>
        <span className="driver-value">Value: {value}</span>
        <span className="driver-percentage" style={{ color: barColor }}>
          {labelPrefix}{impact}%
        </span>
      </div>
      
      <div className="driver-progress-container">
        <div 
          className="driver-progress-fill"
          style={{ 
            width: `${Math.min(100, impact)}%`, 
            backgroundColor: barColor 
          }}
        />
      </div>
    </div>
  );
}
