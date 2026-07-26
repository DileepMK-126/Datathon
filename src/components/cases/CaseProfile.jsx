import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function CaseProfile({ caseProfile }) {
  if (!caseProfile) return null;

  return (
    <>
      <div className="profile-grid">
        <div>
          <span className="profile-label">SOURCE RECORDS</span>
          {caseProfile.sources.map(source => (
            <div className="source-row" key={`${source.source_system}-${source.record_type}`}>
              <strong>{source.source_system}</strong>
              <span>{source.record_type} · {Math.round(source.confidence * 100)}% confidence</span>
            </div>
          ))}
        </div>
        
        <div>
          <span className="profile-label">RESOLVED ENTITIES</span>
          <div className="entity-chips">
            {caseProfile.entities.map(entity => (
              <span key={`${entity.type}-${entity.label}`}>
                {entity.type}: {entity.label}
              </span>
            ))}
          </div>
          <span className="profile-label linked-label">LINKED CASES</span>
          <div className="linked-cases">
            {caseProfile.linked_cases.slice(0, 4).map(item => (
              <span key={item.id}>
                {item.id} · {item.zone_name}
              </span>
            ))}
          </div>
        </div>
      </div>
      
      <div className="integration-note">
        <ShieldCheck size={17}/>
        {caseProfile.integration_note}
      </div>
    </>
  );
}
