import React, { useState } from 'react';
import { Route, Search, HelpCircle, ArrowRight } from 'lucide-react';
import Card from '../common/Card';

export default function PathViewer({ onFindPath }) {
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [pathResult, setPathResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!source || !target) return;

    setLoading(true);
    setError(null);
    setPathResult(null);
    try {
      const res = await fetch(`/api/network/path?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}`);
      if (!res.ok) {
        throw new Error('No connection path found between the selected nodes.');
      }
      const data = await res.json();
      setPathResult(data);
      if (data.path.length > 0) {
        onFindPath(data.path);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Shortest Connection Pathfinder" kicker="RELATIONSHIP ROUTING" className="path-viewer-card">
      <form onSubmit={handleSubmit} className="pathfinder-inputs-form">
        <div className="form-group-row">
          <input 
            type="text" 
            placeholder="Source node ID (e.g. person:A or FIR-7001)"
            value={source}
            onChange={e => setSource(e.target.value)}
            className="input-text-sm"
          />
          <span className="form-arrow-sep"><ArrowRight size={14} /></span>
          <input 
            type="text" 
            placeholder="Target node ID (e.g. person:B)"
            value={target}
            onChange={e => setTarget(e.target.value)}
            className="input-text-sm"
          />
        </div>
        <button type="submit" className="btn btn-primary btn-sm btn-full mt-2" disabled={loading}>
          {loading ? 'Routing...' : 'Analyze Connection Path'}
        </button>
      </form>

      {error && <div className="error-panel mt-2">{error}</div>}

      {pathResult && pathResult.path.length > 0 && (
        <div className="path-results-dossier mt-3">
          <div className="path-hops-count">Connection Chain ({pathResult.length} hops):</div>
          <div className="path-steps-list">
            {pathResult.steps.map((step, idx) => (
              <div key={idx} className="path-step-card">
                <div className="step-nodes-connection">
                  <span className="step-node-item">{step.source}</span>
                  <span className="step-relation-arrow" title={step.explanation}>
                    {step.relation} ({step.confidence}%)
                  </span>
                  <span className="step-node-item">{step.target}</span>
                </div>
                <p className="step-explanation-detail">"{step.description}"</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
