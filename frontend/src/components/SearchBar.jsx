import React, { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';

const SearchBar = ({ neighborhoods, onSelect }) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [filteredResults, setFilteredResults] = useState([]);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Filter neighborhoods based on query
  useEffect(() => {
    if (query.trim().length > 0) {
      const filtered = neighborhoods.filter(n => 
        n.neighborhood?.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 8); // Limit to 8 results
      setFilteredResults(filtered);
      setIsOpen(filtered.length > 0);
    } else {
      setFilteredResults([]);
      setIsOpen(false);
    }
  }, [query, neighborhoods]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target) &&
          inputRef.current && !inputRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (neighborhood) => {
    onSelect(neighborhood);
    setQuery('');
    setIsOpen(false);
  };

  const clearSearch = () => {
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const getActivityClass = (risk) => {
    if (!risk) return 'low';
    const r = risk.toLowerCase();
    if (r.includes('high')) return 'high';
    if (r.includes('medium')) return 'medium';
    return 'low';
  };

  return (
    <div className="search-container" data-testid="search-container">
      <div className="search-input-wrapper">
        <Search size={18} className="search-icon" />
        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder="Search neighborhood..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim().length > 0 && setIsOpen(true)}
          data-testid="search-input"
        />
        {query && (
          <button className="search-clear" onClick={clearSearch}>
            <X size={16} />
          </button>
        )}
      </div>

      {isOpen && filteredResults.length > 0 && (
        <div className="search-dropdown" ref={dropdownRef} data-testid="search-dropdown">
          {filteredResults.map((n, idx) => (
            <div
              key={idx}
              className="search-result-item"
              onClick={() => handleSelect(n)}
              data-testid={`search-result-${idx}`}
            >
              <div className="search-result-name">{n.neighborhood}</div>
              <span className={`search-result-badge ${getActivityClass(n.final_risk)}`}>
                {n.final_risk?.replace(' Risk', '') || 'Lower'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;