import React, { useState } from 'react';
import { Search } from 'lucide-react';

export default function SearchPanel({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="search-panel-container">
      <form onSubmit={handleSearchSubmit} className="search-input-wrapper">
        <input 
          type="text"
          placeholder="Search Case, Person, Phone, Vehicle..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="search-input-field"
        />
        <button type="submit" className="search-submit-btn">
          <Search size={14} />
        </button>
      </form>
    </div>
  );
}
