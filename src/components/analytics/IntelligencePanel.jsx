import React from 'react';
import { Brain, ShieldAlert, ListChecks, Sparkles, CheckCircle2, Loader2 } from 'lucide-react';
import Card from '../common/Card';

export default function IntelligencePanel({ data, loading }) {
  if (loading) {
    return (
      <Card 
        title="Unified intelligence brief" 
        kicker="SENTINEL COGNITIVE ENGINE" 
        className="intelligence-panel loading-state"
        kickerTone="purple"
      >
        <div className="intel-loading">
          <Loader2 className="animate-spin" size={24} style={{ color: '#ad9aff' }} />
          <span>Synthesizing multi-agent intelligence payload...</span>
        </div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card 
        title="Unified intelligence brief" 
        kicker="SENTINEL COGNITIVE ENGINE" 
        className="intelligence-panel empty-state"
        kickerTone="purple"
      >
        <div className="intel-loading">
          <span>Select a zone to generate intelligence brief</span>
        </div>
      </Card>
    );
  }

  // Color mappings based on priority
  const priorityColorMap = {
    CRITICAL: { text: 'critical', border: '#ef5949', bg: '#4d242b', fg: '#ff958b' },
    HIGH: { text: 'high', border: '#ffad4e', bg: '#4a3b20', fg: '#ffc885' },
    MEDIUM: { text: 'watch', border: '#78b5ff', bg: '#243e52', fg: '#7fc1f7' },
    LOW: { text: 'stable', border: '#60be9f', bg: '#1c3d37', fg: '#8ce2c2' }
  };

  const priority = data.priority?.toUpperCase() || 'LOW';
  const styleInfo = priorityColorMap[priority] || priorityColorMap.LOW;

  return (
    <Card 
      title={`Unified intelligence brief — ${data.zone_name}`} 
      kicker="SENTINEL COGNITIVE ENGINE" 
      className="intelligence-panel"
      kickerTone="purple"
    >
      <div className="intel-body">
        <div className="intel-header">
          <div className="intel-badge" style={{ backgroundColor: styleInfo.bg, color: styleInfo.fg, borderColor: styleInfo.border }}>
            <ShieldAlert size={14} />
            <strong>{priority} PRIORITY</strong>
          </div>
          <div className="intel-confidence">
            <span>Confidence:</span>
            <strong>{data.confidence}%</strong>
            <div className="confidence-track">
              <div className="confidence-bar" style={{ width: `${data.confidence}%`, backgroundColor: styleInfo.border }}></div>
            </div>
          </div>
        </div>

        <div className="intel-summary-section">
          <p className="intel-summary-text">{data.summary}</p>
        </div>

        <div className="intel-grid">
          <div className="intel-evidence-box">
            <h3>
              <ListChecks size={15} /> 
              <span>CORROBORATING EVIDENCE</span>
            </h3>
            {data.evidence && data.evidence.length > 0 ? (
              <ul className="evidence-list">
                {data.evidence.map((item, idx) => (
                  <li key={idx}>
                    <span className="bullet-dot" style={{ backgroundColor: styleInfo.border }}></span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-copy">No positive evidence indicators flagged.</p>
            )}
          </div>

          <div className="intel-drivers-box">
            <h3>
              <Brain size={15} /> 
              <span>PRIMARY RISK DRIVERS</span>
            </h3>
            <div className="intel-drivers-chips">
              {data.drivers && data.drivers.length > 0 ? (
                data.drivers.map((driver, idx) => (
                  <span key={idx} className="driver-chip">
                    {driver}
                  </span>
                ))
              ) : (
                <span className="driver-chip empty">Baseline activity</span>
              )}
            </div>
          </div>
        </div>

        {data.recommendations && data.recommendations.length > 0 && (
          <div className="intel-recommendation-box">
            <div className="recommendation-header">
              <Sparkles size={16} />
              <span>RECOMMENDED INTERVENTIONS</span>
            </div>
            <ul className="recommendations-list">
              {data.recommendations.map((action, idx) => (
                <li key={idx}>
                  <strong>Action {idx + 1}:</strong> {action}
                </li>
              ))}
            </ul>
          </div>
        )}

        {data.review_required && (
          <div className="intel-review-footer">
            <CheckCircle2 size={14} />
            <span>Decision-support brief compiled dynamically. Analyst review and verification required before dispatch.</span>
          </div>
        )}
      </div>
    </Card>
  );
}
