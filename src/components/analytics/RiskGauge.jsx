import React from 'react';
import { Sparkles, Users, MoreHorizontal, ChevronDown } from 'lucide-react';
import Card from '../common/Card';

export default function RiskGauge({ 
  activeZone, 
  riskLabel, 
  recommendationData 
}) {
  const dropdownTrigger = (
    <button className="more-button">
      <MoreHorizontal size={20}/>
    </button>
  );

  return (
    <Card 
      title="Area risk forecast" 
      kicker="EXPLAINABLE AI" 
      kickerTone="purple"
      className="risk-panel" 
      headerActions={dropdownTrigger}
    >
      <div className="risk-zone">
        <span>FOCUS AREA</span>
        <button>{activeZone.name}<ChevronDown size={15}/></button>
      </div>
      
      <div className="risk-gauge">
        <svg viewBox="0 0 180 115">
          <path d="M 20 100 A 70 70 0 0 1 160 100" fill="none" stroke="#243142" strokeWidth="15" strokeLinecap="round"/>
          <path 
            d="M 20 100 A 70 70 0 0 1 160 100" 
            fill="none" 
            stroke="url(#gauge-gradient)" 
            strokeWidth="15" 
            strokeLinecap="round" 
            strokeDasharray="220" 
            strokeDashoffset={220 - (220 * activeZone.risk / 100)}
          />
          <defs>
            <linearGradient id="gauge-gradient">
              <stop stopColor="#ffbe55"/>
              <stop offset=".6" stopColor="#ff7749"/>
              <stop offset="1" stopColor="#f14e5d"/>
            </linearGradient>
          </defs>
        </svg>
        <div className="gauge-label">
          <strong>{activeZone.risk}</strong>
          <span>/ 100</span>
          <em>{riskLabel} risk</em>
        </div>
      </div>
      
      <p className="risk-copy">Elevated probability of property crime in the next <b>6 hours</b>.</p>
      
      <div className="drivers">
        <div className="drivers-head">
          <span>TOP RISK DRIVERS</span>
          <button>{activeZone.confidence ? `${activeZone.confidence}% confidence` : 'Why this score?'}</button>
        </div>
        {(activeZone.drivers?.length ? activeZone.drivers : [
          { name: 'Recent burglary pattern', impact: 32 },
          { name: 'Repeat-location frequency', impact: 21 },
          { name: 'Reduced patrol coverage', impact: 12 }
        ]).map((driver) => (
          <div className="driver" key={driver.name}>
            <span>{driver.name}</span>
            <div>
              <i style={{ width: `${Math.min(100, Math.max(18, driver.impact * 1.2))}%` }}></i>
            </div>
            <b>+{driver.impact}</b>
          </div>
        ))}
      </div>
      
      {recommendationData?.actions?.[0] && (
        <div className="action-card">
          <span>RECOMMENDED ACTION</span>
          <strong>{recommendationData.actions[0].action}</strong>
          <p>{recommendationData.actions[0].evidence}</p>
        </div>
      )}
      
      <div className="human-review">
        <Users size={17}/>
        <span>Decision support only — <b>review required</b></span>
      </div>
    </Card>
  );
}
