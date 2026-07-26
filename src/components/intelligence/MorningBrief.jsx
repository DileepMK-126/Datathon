import React, { useState, useEffect } from 'react';
import { Sparkles, FileText, FileJson, ArrowRight, RefreshCw, Printer } from 'lucide-react';
import Loader from '../common/Loader';
import Card from '../common/Card';
import ThreatLevelCard from './ThreatLevelCard';
import BriefSummary from './BriefSummary';
import IntelligenceHighlights from './IntelligenceHighlights';
import ExecutiveMetrics from './ExecutiveMetrics';
import PriorityAlerts from './PriorityAlerts';

export default function MorningBrief({ userRole, onEnterDashboard }) {
  const [briefData, setBriefData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(60); // refresh every 60s
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchMorningBrief = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/intelligence/brief');
      if (!res.ok) {
        throw new Error('Failed to load morning brief details.');
      }
      const data = await res.json();
      setBriefData(data);
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMorningBrief();
  }, []);

  // Auto Refresh Interval effect
  useEffect(() => {
    const timer = setInterval(() => {
      fetchMorningBrief();
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [refreshInterval]);

  const handleExportJson = () => {
    if (!briefData) return;
    const blob = new Blob([JSON.stringify(briefData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `morning-brief-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportMarkdown = () => {
    if (!briefData) return;
    const blob = new Blob([briefData.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `morning-brief-${new Date().toISOString().split('T')[0]}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    alert("Morning Intelligence Brief prepared. Press Ctrl+P/Cmd+P to print report.");
    window.print();
  };

  return (
    <div className="morning-brief-landing-container">
      <div className="brief-header-row">
        <div>
          <div className="brief-eyebrow">
            <Sparkles size={14} className="text-orange" />
            <span>DAILY BRIEFING</span>
          </div>
          <h2>Executive morning intelligence brief</h2>
          <p className="brief-subtitle">Command Center summary and active threat forecasts.</p>
        </div>
        
        <div className="brief-actions-group">
          {lastRefreshed && (
            <span className="last-refreshed-label">
              Last update: {lastRefreshed}
            </span>
          )}
          
          <button className="btn btn-secondary btn-sm" onClick={handleExportJson}>
            <FileJson size={13} />
            <span>Export JSON</span>
          </button>
          
          <button className="btn btn-secondary btn-sm" onClick={handleExportMarkdown}>
            <FileText size={13} />
            <span>Export MD</span>
          </button>
          
          <button className="btn btn-secondary btn-sm" onClick={handlePrint}>
            <Printer size={13} />
            <span>Print Report</span>
          </button>
          
          <button 
            type="button" 
            className="btn btn-primary"
            onClick={onEnterDashboard}
          >
            <span>Enter command center</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {loading && !briefData && <Loader message="Compiling daily command briefs..." />}
      {error && <div className="error-panel">{error}</div>}

      {!error && briefData && (
        <div className="brief-landing-layout">
          {/* Top section: Threat Card & Summary Narrative */}
          <div className="brief-layout-grid-top">
            <ThreatLevelCard 
              threatLevel={briefData.threat_level}
              threatScore={briefData.threat_score}
              highestSector={briefData.highest_risk_sector}
            />
            
            <div className="brief-narrative-card">
              <BriefSummary summary={briefData.summary} />
              <IntelligenceHighlights highlights={briefData.highlights} />
            </div>
          </div>

          {/* Bottom section: Metrics and prioritizing alerts */}
          <div className="brief-layout-grid-bottom">
            <div className="brief-metrics-column">
              <h3 className="brief-section-title">Operational metrics</h3>
              <ExecutiveMetrics metrics={briefData.metrics} />
            </div>
            
            <PriorityAlerts alerts={briefData.alerts} />
          </div>
        </div>
      )}
    </div>
  );
}
