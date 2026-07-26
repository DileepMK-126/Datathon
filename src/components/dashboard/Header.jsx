import React from 'react';
import { Menu, ChevronRight, Search, Bell, ChevronDown } from 'lucide-react';

export default function Header({ onAlertsClick }) {
  return (
    <header className="topbar">
      <button className="mobile-menu">
        <Menu size={21}/>
      </button>
      <div className="breadcrumb">
        <span>Intelligence</span>
        <ChevronRight size={15}/>
        <strong>City overview</strong>
      </div>
      <div className="top-actions">
        <button className="icon-button" aria-label="Search">
          <Search size={20}/>
        </button>
        <button className="icon-button notification" aria-label="Alerts" onClick={onAlertsClick}>
          <Bell size={20}/>
          <i></i>
        </button>
        <button className="city-switch">
          Northbridge City <ChevronDown size={16}/>
        </button>
      </div>
    </header>
  );
}
