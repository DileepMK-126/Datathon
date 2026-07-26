import React from 'react';
import { TrendingUp, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';

export default function ExecutiveMetrics({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="executive-metrics-grid">
      <div className="executive-metric-card">
        <span className="metric-card-kicker">Risk Trend</span>
        <div className="metric-card-value-row">
          <TrendingUp size={16} className="text-violet" />
          <strong className="metric-card-val text-violet">{metrics.risk_trend}</strong>
        </div>
      </div>
      
      <div className="executive-metric-card">
        <span className="metric-card-kicker">Incident Growth</span>
        <strong className="metric-card-val text-orange">
          {metrics.incident_growth >= 0 ? '+' : ''}{metrics.incident_growth}%
        </strong>
      </div>

      <div className="executive-metric-card">
        <span className="metric-card-kicker">Active Hotspots</span>
        <strong className="metric-card-val">{metrics.hotspot_growth}</strong>
      </div>

      <div className="executive-metric-card">
        <span className="metric-card-kicker">Patrol Directives</span>
        <strong className="metric-card-val text-green">{metrics.recommendation_count}</strong>
      </div>
    </div>
  );
}
