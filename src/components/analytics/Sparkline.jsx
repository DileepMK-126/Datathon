import React from 'react';

export default function Sparkline({ values = [] }) {
  if (!values || !values.length) return null;
  const max = Math.max(...values), min = Math.min(...values);
  const range = max - min === 0 ? 1 : max - min;
  const points = values.map((value, index) => `${(index / (values.length - 1)) * 100},${92 - ((value - min) / range) * 74}`).join(' ');
  const fill = `0,100 ${points} 100,100`;
  
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="sparkline" aria-label="Seven day incident trend">
      <defs>
        <linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#ff7c42" stopOpacity=".42"/>
          <stop offset="1" stopColor="#ff7c42" stopOpacity="0"/>
        </linearGradient>
      </defs>
      <polygon points={fill} fill="url(#chart-fill)" />
      <polyline points={points} fill="none" stroke="#ff8755" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
      <line x1="0" y1="32" x2="100" y2="32" stroke="#ffc4a9" strokeDasharray="3 4" strokeOpacity=".35" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
