import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import ChicagoMap from './components/ChicagoMap';
import Legend from './components/Legend';
import SearchBar from './components/SearchBar';
import NeighborhoodDetailsPanel from './components/NeighborhoodDetailsPanel';
import ChatbotPanel from './components/ChatbotPanel';
import NeighborhoodTooltip from './components/NeighborhoodTooltip';
import { 
  loadCSVData, 
  loadGeoJSON, 
  mergeDataWithGeoJSON,
  normalizeNeighborhoodName 
} from './utils/dataLoader';

function App() {
  // Data state
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [neighborhoods, setNeighborhoods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // UI state
  const [activeFilter, setActiveFilter] = useState('all');
  const [hoveredNeighborhood, setHoveredNeighborhood] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState(null);
  const [selectedNeighborhood, setSelectedNeighborhood] = useState(null);
  const [flyToNeighborhood, setFlyToNeighborhood] = useState(null);

  // Load data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        const [csvResult, geoJson] = await Promise.all([
          loadCSVData('/data/herway_final.csv'),
          loadGeoJSON('/data/chicago_neighborhoods.geojson')
        ]);

        const mergedGeoJson = mergeDataWithGeoJSON(geoJson, csvResult.dataMap);
        
        setGeoJsonData(mergedGeoJson);
        setNeighborhoods(csvResult.data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load neighborhood data');
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle hover
  const handleNeighborhoodHover = useCallback((data, position) => {
    setHoveredNeighborhood(data);
    setTooltipPosition(position);
  }, []);

  // Handle click
  const handleNeighborhoodClick = useCallback((data) => {
    console.log('App received click:', data?.neighborhood);
    setSelectedNeighborhood(data);
  }, []);

  // Handle search select - fly to neighborhood and show details
  const handleSearchSelect = useCallback((neighborhood) => {
    setSelectedNeighborhood(neighborhood);
    
    if (geoJsonData) {
      const normalizedSearch = normalizeNeighborhoodName(neighborhood.neighborhood);
      const feature = geoJsonData.features.find(f => 
        normalizeNeighborhoodName(f.properties.community) === normalizedSearch
      );
      
      if (feature && feature.geometry) {
        const coords = feature.geometry.type === 'MultiPolygon' 
          ? feature.geometry.coordinates[0][0]
          : feature.geometry.coordinates[0];
        
        const lats = coords.map(c => c[1]);
        const lngs = coords.map(c => c[0]);
        const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
        const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
        
        setFlyToNeighborhood({
          center: [centerLat, centerLng],
          zoom: 13
        });
        
        setTimeout(() => setFlyToNeighborhood(null), 1000);
      }
    }
  }, [geoJsonData]);

  // Handle close details panel
  const handleCloseDetails = useCallback(() => {
    setSelectedNeighborhood(null);
  }, []);

  // Handle filter change
  const handleFilterChange = useCallback((filter) => {
    setActiveFilter(filter);
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <h2>Loading HerWay...</h2>
        <p>Preparing Chicago neighborhood data</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-container">
        <h2 style={{ color: 'var(--risk-high)' }}>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="app-container" data-testid="app-container">
      {/* Map Section */}
      <div className="map-section">
        <ChicagoMap
          geoJsonData={geoJsonData}
          activeFilter={activeFilter}
          selectedNeighborhood={selectedNeighborhood}
          onNeighborhoodHover={handleNeighborhoodHover}
          onNeighborhoodClick={handleNeighborhoodClick}
          flyToNeighborhood={flyToNeighborhood}
          onFilterChange={handleFilterChange}
        />

        {/* Search Bar */}
        <SearchBar 
          neighborhoods={neighborhoods} 
          onSelect={handleSearchSelect} 
        />

        {/* Legend */}
        <Legend />

        {/* Details Panel - Shows when neighborhood is selected */}
        {selectedNeighborhood && (
          <NeighborhoodDetailsPanel
            data={selectedNeighborhood}
            onClose={handleCloseDetails}
          />
        )}

        {/* Hover Tooltip */}
        {hoveredNeighborhood && tooltipPosition && !selectedNeighborhood && (
          <NeighborhoodTooltip data={hoveredNeighborhood} position={tooltipPosition} />
        )}
      </div>

      {/* Chatbot Panel */}
      <ChatbotPanel selectedNeighborhood={selectedNeighborhood} />
    </div>
  );
}

export default App;