import React from 'react';
import { Filter, Eye, RefreshCw, ZoomIn, ZoomOut } from 'lucide-react';

export default function GraphControls({
  nodeTypes,
  selectedNodeTypes,
  onNodeTypeToggle,
  onResetLayout,
  onZoomIn,
  onZoomOut
}) {
  return (
    <div className="graph-controls-panel">
      <div className="controls-section-title">
        <Filter size={14} />
        <span>Graph Filter & Operations</span>
      </div>
      
      {/* Node Type Filters */}
      <div className="node-filters-group">
        <span className="filters-sub-label">Include Entity Types:</span>
        <div className="filters-checkbox-grid">
          {nodeTypes.map(type => {
            const isChecked = selectedNodeTypes.includes(type);
            return (
              <label key={type} className={`filter-chip-label ${isChecked ? 'active' : ''}`}>
                <input 
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => onNodeTypeToggle(type)}
                  style={{ display: 'none' }}
                />
                <span>{type}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="controls-actions-row">
        <button className="btn btn-secondary btn-sm" onClick={onZoomIn} title="Zoom In">
          <ZoomIn size={14} />
        </button>
        <button className="btn btn-secondary btn-sm" onClick={onZoomOut} title="Zoom Out">
          <ZoomOut size={14} />
        </button>
        <button className="btn btn-secondary btn-sm" onClick={onResetLayout} title="Recenter Graph">
          <RefreshCw size={14} />
          <span>Recenter</span>
        </button>
      </div>
    </div>
  );
}
