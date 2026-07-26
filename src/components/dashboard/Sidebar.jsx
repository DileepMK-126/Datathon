import React from 'react';
import { Layers3, MapPin, Network, Activity, FileText, CircleHelp, ShieldCheck, MoreHorizontal } from 'lucide-react';

export default function Sidebar({ onNetworkClick, onLogout, onDemoClick }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <ShieldCheck size={23}/>
        </div>
        <span>SENTINEL</span>
      </div>
      <div className="workspace-label">COMMAND CENTER</div>
      <nav className="nav-list" aria-label="Primary navigation">
        <button className="nav-item active">
          <Layers3 size={19}/>
          <span>Overview</span>
        </button>
        <button className="nav-item">
          <MapPin size={19}/>
          <span>Geospatial Intel</span>
        </button>
        <button className="nav-item" onClick={onNetworkClick}>
          <Network size={19}/>
          <span>Case Networks</span>
        </button>
        <button className="nav-item text-orange" onClick={onDemoClick} style={{ color: '#f59e0b' }}>
          <Activity size={19}/>
          <span>Walkthrough Walk</span>
        </button>
        <button className="nav-item">
          <Activity size={19}/>
          <span>Trend Analysis</span>
        </button>
        <button className="nav-item">
          <FileText size={19}/>
          <span>Case Records</span>
        </button>
      </nav>
      <div className="sidebar-bottom">
        <button className="nav-item" onClick={onLogout} style={{ marginTop: 'auto' }}>
          <CircleHelp size={19}/>
          <span>Sign out</span>
        </button>
        <div className="officer-card">
          <div className="avatar">AM</div>
          <div>
            <strong>Arjun Mehta</strong>
            <span>Duty Analyst</span>
          </div>
          <MoreHorizontal size={18}/>
        </div>
      </div>
    </aside>
  );
}
