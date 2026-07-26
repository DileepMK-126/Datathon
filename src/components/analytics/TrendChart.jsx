import React from 'react';
import { Activity, AlertTriangle, ChevronRight } from 'lucide-react';
import Card from '../common/Card';
import Sparkline from './Sparkline';

export default function TrendChart({ 
  period, 
  setPeriod, 
  trendData, 
  defaultTrend 
}) {
  const periodSelector = (
    <select value={period} onChange={e => setPeriod(e.target.value)} aria-label="Trend period">
      <option>24 hours</option>
      <option>7 days</option>
      <option>30 days</option>
    </select>
  );

  return (
    <Card 
      title="Incident volume trend" 
      kicker="ANOMALY MONITORING" 
      kickerTone="orange"
      className="trend-panel"
      headerActions={periodSelector}
    >
      <div className="trend-stat">
        <strong>{trendData?.change_percent >= 0 ? '+' : ''}{trendData?.change_percent ?? 38}%</strong>
        <span>above expected baseline</span>
        <div className="trend-key"><i></i> Actual <b></b> Expected</div>
      </div>
      
      <div className="chart-wrap">
        <Sparkline values={trendData?.actual ?? defaultTrend} />
      </div>
      
      <div className="chart-axis">
        {(trendData?.labels ?? ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']).slice(-7).map(label => (
          <span key={label}>{label.slice(-2)}</span>
        ))}
      </div>
      
      <div className="anomaly-callout">
        <AlertTriangle size={18}/>
        <div>
          <strong>{trendData?.anomaly?.detected ? 'Anomaly detected' : 'Pattern monitored'}</strong>
          <span>
            {trendData?.anomaly?.dates?.[0] 
              ? `Isolation Forest flagged ${trendData.anomaly.dates[0]}` 
              : 'Unusual rise begins Friday 18:00'
            }
          </span>
        </div>
        <ChevronRight size={18}/>
      </div>
    </Card>
  );
}
