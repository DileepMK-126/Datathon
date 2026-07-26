import React from 'react';
import { AlertCircle, Clock } from 'lucide-react';

export default function PriorityAlerts({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="priority-alerts-section">
      <h3 className="priority-alerts-title">Prioritized Operational Alerts</h3>
      <div className="priority-alerts-list">
        {alerts.map(alert => (
          <div key={alert.id} className={`priority-alert-card level-${alert.level}`}>
            <div className="alert-card-header">
              <span className={`alert-level-badge level-${alert.level}`}>{alert.level}</span>
              <div className="alert-card-time">
                <Clock size={12} />
                <span>{alert.detected}</span>
              </div>
            </div>
            <h4 className="alert-card-title">{alert.title}</h4>
            <p className="alert-card-text">{alert.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
