import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function ThreatLevelCard({ threatLevel, threatScore, highestSector }) {
  const getThreatClass = () => {
    switch (threatLevel.toLowerCase()) {
      case 'critical': return 'brief-threat-critical';
      case 'high': return 'brief-threat-high';
      case 'elevated': return 'brief-threat-elevated';
      default: return 'brief-threat-guarded';
    }
  };

  return (
    <div className={`brief-threat-card ${getThreatClass()}`}>
      <div className="brief-threat-header">
        <ShieldAlert size={28} />
        <div className="brief-threat-title-group">
          <span className="brief-threat-kicker">OVERALL THREAT LEVEL</span>
          <strong className="brief-threat-val">{threatLevel}</strong>
        </div>
      </div>
      
      <div className="brief-threat-score-row">
        <span className="threat-score-label">Threat Index:</span>
        <strong className="threat-score-val">{threatScore}/100</strong>
      </div>
      
      <div className="brief-threat-sector-row">
        <span className="threat-sector-label">Highest Risk Sector:</span>
        <strong className="threat-sector-val">{highestSector}</strong>
      </div>
    </div>
  );
}
