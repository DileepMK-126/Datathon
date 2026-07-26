import React, { useState, useMemo } from 'react';
import { 
  Shield, Camera, Scale, Brain, Compass, Calendar, 
  ChevronDown, ChevronUp, Filter, Clock, User, AlertTriangle, FileText, CheckCircle
} from 'lucide-react';
import Card from '../common/Card';

export default function TimelinePanel({ data, loading }) {
  const [expandedEvents, setExpandedEvents] = useState({});
  const [filterSource, setFilterSource] = useState('ALL');
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [sortOrder, setSortOrder] = useState('ASC');

  // Toggle single event details expand/collapse
  const toggleExpand = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // Icon resolver based on source system / event type
  const getEventIcon = (sourceSystem) => {
    const sys = sourceSystem.toLowerCase();
    if (sys.includes('fir') || sys.includes('police')) {
      return <Shield size={16} className="text-blue" />;
    }
    if (sys.includes('cctv') || sys.includes('camera')) {
      return <Camera size={16} className="text-orange" />;
    }
    if (sys.includes('court') || sys.includes('judge')) {
      return <Scale size={16} className="text-purple" />;
    }
    if (sys.includes('prison') || sys.includes('correctional')) {
      return <Shield size={16} className="text-red" style={{ color: '#ff6b6b' }} />;
    }
    if (sys.includes('ai') || sys.includes('intel') || sys.includes('cognitive')) {
      return <Brain size={16} className="text-violet" style={{ color: '#c084fc' }} />;
    }
    if (sys.includes('recommendation') || sys.includes('action')) {
      return <Compass size={16} className="text-teal" style={{ color: '#2dd4bf' }} />;
    }
    return <FileText size={16} className="text-slate" />;
  };

  // Color mappings based on severity level
  const severityColors = {
    CRITICAL: { bg: '#4d242b', border: '#ef5949', fg: '#ff958b' },
    HIGH: { bg: '#4a3b20', border: '#ffad4e', fg: '#ffc885' },
    MEDIUM: { bg: '#1c3144', border: '#78b5ff', fg: '#7fc1f7' },
    LOW: { bg: '#1c3d37', border: '#60be9f', fg: '#8ce2c2' }
  };

  // Format standard date strings
  const formatDate = (isoStr) => {
    try {
      const date = new Date(isoStr);
      return date.toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    } catch {
      return isoStr;
    }
  };

  // Format standard time strings
  const formatTime = (isoStr) => {
    try {
      const date = new Date(isoStr);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch {
      return '';
    }
  };

  // Extract unique sources for filter dropdown options
  const sourceOptions = useMemo(() => {
    if (!data?.events) return [];
    const sources = data.events.map(e => e.source_system);
    return ['ALL', ...new Set(sources)];
  }, [data]);

  // Filter and sort events list
  const processedEvents = useMemo(() => {
    if (!data?.events) return [];
    
    let filtered = [...data.events];

    // Filter by Source System
    if (filterSource !== 'ALL') {
      filtered = filtered.filter(e => e.source_system === filterSource);
    }

    // Filter by Severity
    if (filterSeverity !== 'ALL') {
      filtered = filtered.filter(e => e.severity.toUpperCase() === filterSeverity);
    }

    // Sort order (Chrono vs Reverse Chrono)
    filtered.sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime();
      const timeB = new Date(b.timestamp).getTime();
      return sortOrder === 'ASC' ? timeA - timeB : timeB - timeA;
    });

    return filtered;
  }, [data, filterSource, filterSeverity, sortOrder]);

  if (loading) {
    return (
      <Card 
        title="Unified case timeline" 
        kicker="CHRONOLOGICAL CASE STREAM" 
        className="timeline-panel loading-state"
        kickerTone="purple"
      >
        <div className="intel-loading">
          <div className="pulse-dot"></div>
          <span>Consolidating cross-system databases...</span>
        </div>
      </Card>
    );
  }

  if (!data || !data.events || data.events.length === 0) {
    return (
      <Card 
        title="Unified case timeline" 
        kicker="CHRONOLOGICAL CASE STREAM" 
        className="timeline-panel empty-state"
        kickerTone="purple"
      >
        <div className="intel-loading">
          <span>No historical records or updates matched for this dossier case.</span>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title={`Unified case timeline — ${data.case_id}`} 
      kicker="CHRONOLOGICAL CASE STREAM" 
      className="timeline-panel"
      kickerTone="purple"
    >
      <div className="timeline-body">
        
        {/* Interactive Filters Controls bar */}
        <div className="timeline-filters">
          <div className="filter-group">
            <label htmlFor="source-filter"><Filter size={12} /> Source</label>
            <select 
              id="source-filter"
              value={filterSource} 
              onChange={(e) => setFilterSource(e.target.value)}
            >
              {sourceOptions.map(src => (
                <option key={src} value={src}>{src}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="severity-filter"><AlertTriangle size={12} /> Severity</label>
            <select 
              id="severity-filter"
              value={filterSeverity} 
              onChange={(e) => setFilterSeverity(e.target.value)}
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-filter"><Calendar size={12} /> Order</label>
            <select 
              id="sort-filter"
              value={sortOrder} 
              onChange={(e) => setSortOrder(e.target.value)}
            >
              <option value="ASC">Chronological (Oldest First)</option>
              <option value="DESC">Reverse (Newest First)</option>
            </select>
          </div>
        </div>

        {/* Vertical Timeline container */}
        <div className="timeline-container">
          <div className="timeline-line"></div>
          
          <div className="timeline-list">
            {processedEvents.map((evt, index) => {
              const isExpanded = !!expandedEvents[evt.event_id];
              const sev = evt.severity?.toUpperCase() || 'LOW';
              const sevStyle = severityColors[sev] || severityColors.LOW;

              return (
                <div 
                  key={evt.event_id} 
                  className={`timeline-item ${isExpanded ? 'expanded' : ''}`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  
                  {/* Left Column: Date & Time */}
                  <div className="timeline-time">
                    <span className="date-badge">{formatDate(evt.timestamp)}</span>
                    <span className="time-badge"><Clock size={11} /> {formatTime(evt.timestamp)}</span>
                  </div>

                  {/* Center Node (Clickable Icon Node) */}
                  <button 
                    className="timeline-node" 
                    onClick={() => toggleExpand(evt.event_id)}
                    style={{ borderColor: sevStyle.border, boxShadow: `0 0 10px ${sevStyle.border}30` }}
                    aria-label={`Toggle details for ${evt.title}`}
                    aria-expanded={isExpanded}
                  >
                    {getEventIcon(evt.source_system)}
                  </button>

                  {/* Right Column: Event Content Card */}
                  <div 
                    className="timeline-card"
                    style={{ borderLeft: `3px solid ${sevStyle.border}` }}
                    onClick={() => toggleExpand(evt.event_id)}
                  >
                    <div className="card-header-row">
                      <div>
                        <span className="source-label">{evt.source_system.toUpperCase()}</span>
                        <h4>{evt.title}</h4>
                      </div>
                      <div className="badge-row">
                        <span 
                          className="severity-pill"
                          style={{ backgroundColor: sevStyle.bg, color: sevStyle.fg, borderColor: sevStyle.border }}
                        >
                          {sev}
                        </span>
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>

                    <p className="event-teaser">
                      {isExpanded ? evt.description : `${evt.description.substring(0, 100)}...`}
                    </p>

                    {/* Expandable Meta details drawer */}
                    {isExpanded && (
                      <div className="expanded-details" onClick={(e) => e.stopPropagation()}>
                        <div className="detail-meta-grid">
                          <div>
                            <span>System Record</span>
                            <b>{evt.event_type}</b>
                          </div>
                          <div>
                            <span>Confidence Index</span>
                            <b>{Math.round(evt.confidence * 100)}%</b>
                          </div>
                          <div>
                            <span>Case Reference</span>
                            <b>{evt.linked_case || 'N/A'}</b>
                          </div>
                        </div>

                        {evt.resolved_entities && evt.resolved_entities.length > 0 && (
                          <div className="detail-section">
                            <h5>RESOLVED IDENTITY LINKS</h5>
                            <div className="entity-pills">
                              {evt.resolved_entities.map((ent, idx) => (
                                <span key={idx} className="ent-pill">
                                  <User size={10} /> {ent}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {evt.supporting_evidence && evt.supporting_evidence.length > 0 && (
                          <div className="detail-section">
                            <h5>CORROBORATING EVIDENCE LOGS</h5>
                            <ul className="evidence-logs-list">
                              {evt.supporting_evidence.map((evd, idx) => (
                                <li key={idx}>
                                  <CheckCircle size={11} style={{ color: '#8ce2c2' }} />
                                  <span>{evd}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="timeline-footer">
          <span>Active timeline compile: <b>{processedEvents.length} events</b> displayed</span>
        </div>
      </div>
    </Card>
  );
}
