import React from 'react';
import { Shield, Eye, Network, Trash2 } from 'lucide-react';
import Card from '../common/Card';

export default function NodeInspector({ node, onExpand, onCollapse, onClose }) {
  if (!node) {
    return (
      <Card className="node-inspector-card" title="Node Inspector" kicker="SELECTION DETAILS">
        <div className="inspector-empty-state">
          Click any graph node to inspect relationship details, centralities, and evidence traces.
        </div>
      </Card>
    );
  }

  return (
    <Card 
      className="node-inspector-card selected" 
      title={node.label} 
      kicker={node.kind.toUpperCase()}
      kickerTone="violet"
    >
      <div className="inspector-attributes-grid">
        <div className="inspector-attr-row">
          <span className="attr-label">Node ID:</span>
          <code className="attr-val">{node.id}</code>
        </div>
        <div className="inspector-attr-row">
          <span className="attr-label">Degree Centrality:</span>
          <span className="attr-val text-violet">{(node.centrality * 100).toFixed(1)}%</span>
        </div>
        {node.zone_id && (
          <div className="inspector-attr-row">
            <span className="attr-label">Zone Context:</span>
            <span className="attr-val">{node.zone_id}</span>
          </div>
        )}
      </div>

      <div className="inspector-actions-row">
        <button className="btn btn-primary btn-sm flex-grow" onClick={() => onExpand(node.id)}>
          <Network size={13} />
          <span>Expand Neighbors</span>
        </button>
        <button className="btn btn-secondary btn-sm" onClick={() => onCollapse(node.id)}>
          <Trash2 size={13} />
          <span>Collapse</span>
        </button>
      </div>
    </Card>
  );
}
