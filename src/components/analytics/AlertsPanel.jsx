import React from 'react';
import { Bell, AlertTriangle, Network, ShieldCheck, ChevronRight } from 'lucide-react';
import Card from '../common/Card';

export default function AlertsPanel({ 
  displayAlerts, 
  onViewAllAlerts, 
  onOpenAlert 
}) {
  const viewAllButton = (
    <button className="text-button" onClick={onViewAllAlerts}>
      View all
    </button>
  );

  const getIcon = (type, index) => {
    if (type === 'Anomaly' || index === 0) return <AlertTriangle size={18}/>;
    if (type === 'Network' || index === 1) return <Network size={18}/>;
    return <ShieldCheck size={18}/>;
  };

  return (
    <Card 
      title="Intelligence alerts" 
      kicker="PRIORITY QUEUE" 
      kickerTone="red"
      className="alerts-panel"
      headerActions={viewAllButton}
    >
      <div className="alert-list">
        {displayAlerts.map((alert, index) => (
          <button 
            className="alert-row" 
            key={alert.id ?? alert.title} 
            onClick={() => onOpenAlert(alert)}
          >
            <div className={`alert-symbol ${alert.level}`}>
              {getIcon(alert.type, index)}
            </div>
            <div>
              <span className={`type-label ${alert.level}`}>{alert.type}</span>
              <strong>{alert.title}</strong>
              <p>{alert.text}</p>
              <time>{alert.detected ?? alert.time}</time>
            </div>
            <ChevronRight size={18}/>
          </button>
        ))}
      </div>
    </Card>
  );
}
