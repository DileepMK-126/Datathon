import React, { useState, useEffect, useRef } from 'react';
import { Search, Command, Play, RotateCcw, AlertTriangle } from 'lucide-react';

export default function CommandPalette({ isOpen, onClose, onActionTrigger }) {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const commandItems = [
    { id: 'start-walkthrough', name: 'Launch Presentation Walkthrough', desc: 'Starts the guided demo progression scenario.', icon: <Play size={14} className="text-orange" /> },
    { id: 'clear-cache', name: 'Clear Cache Tables', desc: 'Resets memory-stored models and prediction matrices.', icon: <RotateCcw size={14} className="text-violet" /> },
    { id: 'inspect-sector-7', name: 'Focus Sector 7 Zone', desc: 'Focuses maps and charts on Sector 7.', icon: <Search size={14} className="text-blue" /> },
    { id: 'inspect-old-town', name: 'Focus Old Town Zone', desc: 'Focuses maps and charts on Old Town.', icon: <Search size={14} className="text-blue" /> }
  ];

  const filteredCommands = commandItems.filter(item => 
    item.name.toLowerCase().includes(query.toLowerCase()) || 
    item.desc.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (itemId) => {
    onActionTrigger(itemId);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette-dialog" onClick={e => e.stopPropagation()}>
        <div className="command-palette-input-row">
          <Search size={16} className="text-muted" />
          <input 
            ref={inputRef}
            type="text" 
            placeholder="Type a command or search (e.g. walkthrough, cache)..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="command-palette-input"
          />
          <kbd className="command-palette-esc-badge">ESC</kbd>
        </div>

        <div className="command-palette-results-list">
          {filteredCommands.length === 0 ? (
            <div className="command-palette-empty-state">No commands found.</div>
          ) : (
            filteredCommands.map(item => (
              <button 
                key={item.id} 
                className="command-palette-item"
                onClick={() => handleSelect(item.id)}
              >
                <div className="command-palette-item-left">
                  {item.icon}
                  <div className="command-palette-item-text">
                    <span className="command-palette-item-name">{item.name}</span>
                    <span className="command-palette-item-desc">{item.desc}</span>
                  </div>
                </div>
                <span className="command-palette-item-action">Select</span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
