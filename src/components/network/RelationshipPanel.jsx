import React from 'react';
import { Network, Link2 } from 'lucide-react';
import Card from '../common/Card';

export default function RelationshipPanel({ link }) {
  if (!link) return null;

  return (
    <Card title="Relationship Inspector" kicker="CONNECTION DETAILS" className="relationship-panel-card">
      <div className="relationship-attributes-grid">
        <div className="inspector-attr-row">
          <span className="attr-label">Source Node:</span>
          <span className="attr-val">{link.source}</span>
        </div>
        <div className="inspector-attr-row">
          <span className="attr-label">Target Node:</span>
          <span className="attr-val">{link.target}</span>
        </div>
        <div className="inspector-attr-row">
          <span className="attr-label">Relation:</span>
          <strong className="attr-val text-orange">{link.relation}</strong>
        </div>
        <div className="inspector-attr-row">
          <span className="attr-label">Link Confidence:</span>
          <span className="attr-val font-bold text-green">{link.confidence}%</span>
        </div>
      </div>
    </Card>
  );
}
