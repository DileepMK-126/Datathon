import React from 'react';
import { Target, Zap, Shield } from 'lucide-react';

export default function ImpactCard({ deterrence, responseTime, trustIndex }) {
  return (
    <div className="impact-card-container">
      <div className="impact-card-title">Expected Operational Impact</div>
      <div className="impact-metrics-grid">
        <div className="impact-metric-item">
          <Shield size={14} className="text-orange" />
          <span className="impact-label">Deterrence:</span>
          <span className="impact-val">{deterrence}</span>
        </div>
        <div className="impact-metric-item">
          <Zap size={14} className="text-violet" />
          <span className="impact-label">Response Red.:</span>
          <span className="impact-val">{responseTime}</span>
        </div>
        <div className="impact-metric-item">
          <Target size={14} className="text-green" />
          <span className="impact-label">Trust Index:</span>
          <span className="impact-val">{trustIndex}</span>
        </div>
      </div>
    </div>
  );
}
