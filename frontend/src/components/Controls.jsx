import React, { useState, useMemo } from 'react';
import { Search, X } from 'lucide-react';
import { formatNumber } from '../utils/dataLoader';

const Controls = ({ 
  neighborhoods, 
  activeFilter, 
  onFilterChange, 
  onSearchSelect 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showResults, setShowResults] = useState(false);

  const filteredNeighborhoods = useMemo(() => {
    if (!searchTerm.trim() || !neighborhoods) return [];
    
    const term = searchTerm.toLowerCase();
    return neighborhoods
      .filter(n => n.neighborhood && n.neighborhood.toLowerCase().includes(term))
      .slice(0, 8);
  }, [searchTerm, neighborhoods]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setShowResults(true);
  };

  const handleResultClick = (neighborhood) => {
    setSearchTerm(neighborhood.neighborhood);
    setShowResults(false);
    onSearchSelect(neighborhood);
  };

  const clearSearch = () => {
    setSearchTerm('');
    setShowResults(false);
  };

  const filters = [
    { key: 'all', label: 'All Areas' },
    { key: 'high', label: 'High Activity' },
    { key: 'medium', label: 'Moderate' },
    { key: 'low', label: 'Lower' }
  ];

  return (
    <>
      {/* Search Bar */}
      <div className="floating-ui search-bar" data-testid="search-bar">
        <Search size={18} className="search-icon" />
        <input
          type="text"
          placeholder="Search neighborhoods..."
          value={searchTerm}
          onChange={handleSearchChange}
          onFocus={() => setShowResults(true)}
          data-testid="search-input"
        />
        {searchTerm && (
          <button 
            onClick={clearSearch} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
            data-testid="search-clear"
          >
            <X size={16} />
          </button>
        )}
        
        {showResults && filteredNeighborhoods.length > 0 && (
          <div className="search-results" data-testid="search-results">
            {filteredNeighborhoods.map((n, idx) => (
              <div
                key={idx}
                className="search-result-item"
                onClick={() => handleResultClick(n)}
                data-testid={`search-result-${idx}`}
              >
                <span>{n.neighborhood}</span>
                <span className="search-result-info">
                  {formatNumber(n.crime_total_incidents)} incidents
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Activity Filter */}
      <div className="floating-ui risk-filter" data-testid="risk-filter">
        {filters.map(filter => (
          <button
            key={filter.key}
            className={`filter-button ${activeFilter === filter.key ? 'active' : ''}`}
            onClick={() => onFilterChange(filter.key)}
            data-testid={`filter-${filter.key}`}
          >
            {filter.label}
          </button>
        ))}
      </div>
    </>
  );
};

export default Controls;


