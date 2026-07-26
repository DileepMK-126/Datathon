import React from 'react';
import { GitCompare, ExternalLink, Calendar, MapPin, Eye } from 'lucide-react';
import SimilarityBadge from './SimilarityBadge';
import SimilarityExplanation from './SimilarityExplanation';

export default function CaseSimilarityCard({ 
  match, 
  onCompare, 
  onOpenCase,
  userRole 
}) {
  const { case_id, similarity_score, confidence, reasoning, shared_entities, details } = match;

  const getEntityIcon = (type) => {
    return <span className="entity-indicator-tag">{type}</span>;
  };

  const hasSharedEntities = Object.values(shared_entities).some(arr => arr && arr.length > 0);

  return (
    <div className="similarity-card glass-panel fade-in">
      <div className="similarity-card-header">
        <div className="case-info">
          <span className="case-id-kicker">{case_id}</span>
          <span className="crime-type-label">{match.crime_type}</span>
        </div>
        <SimilarityBadge score={similarity_score} confidence={confidence} />
      </div>

      <div className="similarity-card-body">
        <SimilarityExplanation reasoning={reasoning} />

        <div className="meta-row">
          <div className="meta-item">
            <Calendar size={12} />
            <span>{details.incident_date} {details.incident_time}</span>
          </div>
          <div className="meta-item">
            <MapPin size={12} />
            <span>{details.police_station}</span>
          </div>
        </div>

        {hasSharedEntities && (
          <div className="shared-entities-section">
            <div className="shared-entities-label">Shared Resolved Entities:</div>
            <div className="shared-entities-tags">
              {shared_entities.phones && shared_entities.phones.map(p => (
                <span key={p} className="shared-tag phone-tag">📞 {p}</span>
              ))}
              {shared_entities.vehicles && shared_entities.vehicles.map(v => (
                <span key={v} className="shared-tag vehicle-tag">🚗 {v}</span>
              ))}
              {shared_entities.persons && shared_entities.persons.map(pe => (
                <span key={pe} className="shared-tag person-tag">👤 {pe}</span>
              ))}
              {shared_entities.addresses && shared_entities.addresses.map(a => (
                <span key={a} className="shared-tag address-tag">📍 {a}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="similarity-card-actions">
        <button 
          className="btn btn-secondary btn-sm"
          onClick={() => onCompare(match)}
          title="Compare cases side-by-side"
        >
          <GitCompare size={14} />
          <span>Quick Compare</span>
        </button>
        <button 
          className="btn btn-primary btn-sm"
          onClick={() => onOpenCase(case_id)}
          title="Open unified case profile"
        >
          <Eye size={14} />
          <span>View Profile</span>
        </button>
      </div>
    </div>
  );
}
