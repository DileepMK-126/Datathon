import React, { useState, useEffect } from 'react';
import { Network, Download, FileJson, ZoomIn, ZoomOut } from 'lucide-react';
import Loader from '../common/Loader';
import GraphControls from './GraphControls';
import NodeInspector from './NodeInspector';
import RelationshipPanel from './RelationshipPanel';
import PathViewer from './PathViewer';
import CommunityLegend from './CommunityLegend';
import SearchPanel from './SearchPanel';
import { getApi } from '../../services/api';

export default function NetworkGraph({ caseId, userRole }) {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Selection States
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedLink, setSelectedLink] = useState(null);
  const [highlightedPath, setHighlightedPath] = useState([]);
  
  // Filters & Search
  const [selectedNodeTypes, setSelectedNodeTypes] = useState(["Person", "FIR", "Vehicle", "Phone", "Address"]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Zoom & Pan offset
  const [zoom, setZoom] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });

  const fetchGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const typesParams = selectedNodeTypes.map(t => `node_types=${t}`).join('&');
      const searchParam = searchQuery ? `&search_query=${encodeURIComponent(searchQuery)}` : '';
      
      const endpoint = caseId 
        ? `/network/${caseId}?radius=2` 
        : `/network?${typesParams}${searchParam}`;
        
      const data = await getApi(endpoint);
      setGraphData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, [caseId, selectedNodeTypes, searchQuery]);

  const handleNodeTypeToggle = (type) => {
    setSelectedNodeTypes(prev => 
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const handleExport = (format) => {
    if (userRole !== 'supervisor' && userRole !== 'admin') {
      alert("Permission denied. Only Supervisors and Administrators can export graph configurations.");
      return;
    }
    window.open(`/api/network/export?format=${format}`);
  };

  // Modern node coloring based on community or kind
  const colors = ["#a855f7", "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#6366f1", "#ec4899", "#14b8a6"];
  const getNodeColor = (node) => {
    if (highlightedPath.includes(node.id)) return '#ef5949'; // Red for path
    return colors[node.community % colors.length];
  };

  const getNodeRadius = (node) => {
    if (node.id === caseId) return 18; // Primary focus case
    return node.kind === 'FIR' ? 14 : 10;
  };

  return (
    <div className="network-dashboard-container">
      <div className="network-header-row">
        <h3>Criminal Network Intelligence Map</h3>
        
        <div className="network-actions-group">
          <SearchPanel onSearch={setSearchQuery} />
          
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => handleExport('json')}
            title="Export JSON Configuration"
          >
            <FileJson size={13} />
            <span>Export JSON</span>
          </button>
          <button 
            className="btn btn-primary btn-sm"
            onClick={() => handleExport('graphml')}
            title="Export GraphML XML"
          >
            <Download size={13} />
            <span>Export GraphML</span>
          </button>
        </div>
      </div>

      <div className="network-workspace-split">
        {/* Left pane: Control Widgets */}
        <div className="network-control-pane">
          <GraphControls 
            nodeTypes={["Person", "FIR", "Vehicle", "Phone", "Address"]}
            selectedNodeTypes={selectedNodeTypes}
            onNodeTypeToggle={handleNodeTypeToggle}
            onResetLayout={() => { setZoom(1); setPanOffset({ x: 0, y: 0 }); setHighlightedPath([]); }}
            onZoomIn={() => setZoom(z => Math.min(2.5, z + 0.15))}
            onZoomOut={() => setZoom(z => Math.max(0.5, z - 0.15))}
          />
          
          <PathViewer onFindPath={setHighlightedPath} />
          
          <NodeInspector 
            node={selectedNode}
            onExpand={(id) => fetchGraphData()}
            onCollapse={() => setSelectedNode(null)}
          />
          
          <RelationshipPanel link={selectedLink} />
        </div>

        {/* Right pane: Interactive SVG Canvas */}
        <div className="network-graph-canvas-card">
          {loading && <Loader message="Rendering intelligence topology..." />}
          {error && <div className="error-panel">{error}</div>}

          {!loading && !error && graphData && (
            <div className="svg-canvas-wrapper">
              <svg 
                className="network-svg-canvas"
                viewBox="0 0 800 500"
                width="100%"
                height="100%"
              >
                {/* 1. Draw Links */}
                <g className="network-links-group">
                  {graphData.links.map((link, idx) => {
                    const sourcePos = graphData.layout[link.source] ?? [400, 250];
                    const targetPos = graphData.layout[link.target] ?? [400, 250];
                    const isHighlighted = highlightedPath.includes(link.source) && highlightedPath.includes(link.target);
                    
                    return (
                      <line 
                        key={idx}
                        x1={sourcePos[0]}
                        y1={sourcePos[1]}
                        x2={targetPos[0]}
                        y2={targetPos[1]}
                        className={`network-graph-edge ${isHighlighted ? 'highlighted' : ''}`}
                        stroke={isHighlighted ? '#ef5949' : 'rgba(255,255,255,0.08)'}
                        strokeWidth={isHighlighted ? 3 : 1.5}
                        onClick={() => setSelectedLink(link)}
                      />
                    );
                  })}
                </g>

                {/* 2. Draw Nodes */}
                <g className="network-nodes-group">
                  {graphData.nodes.map(node => {
                    const pos = graphData.layout[node.id] ?? [400, 250];
                    const r = getNodeRadius(node);
                    const color = getNodeColor(node);
                    const isSelected = selectedNode?.id === node.id;
                    const isPathHighlighted = highlightedPath.includes(node.id);
                    
                    return (
                      <g 
                        key={node.id} 
                        transform={`translate(${pos[0]}, ${pos[1]})`}
                        onClick={() => setSelectedNode(node)}
                        className={`graph-node-group ${isSelected ? 'selected' : ''}`}
                      >
                        <circle 
                          r={r} 
                          fill={color}
                          stroke={isSelected ? '#ffffff' : isPathHighlighted ? '#ef5949' : 'rgba(0,0,0,0.5)'}
                          strokeWidth={isSelected || isPathHighlighted ? 3 : 1}
                        />
                        <text 
                          dy="24"
                          textAnchor="middle"
                          fill="var(--text-muted, #94a3b8)"
                          fontSize="9"
                          fontWeight={isSelected ? 'bold' : 'normal'}
                        >
                          {node.label}
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>
              
              <CommunityLegend communities={[]} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
