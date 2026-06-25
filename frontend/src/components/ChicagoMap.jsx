// Core HerWay map component enabling neighborhood exploration through spatial activity and risk indicators
import React, { useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const MapController = ({ flyTo }) => {
  const map = useMap();
  
  useEffect(() => {
    if (flyTo) {
      map.flyTo(flyTo.center, flyTo.zoom || 12, { duration: 0.8 });
    }
  }, [flyTo, map]);
  
  return null;
};

const ChicagoMap = ({ 
  geoJsonData, 
  activeFilter,
  selectedNeighborhood,
  onNeighborhoodHover, 
  onNeighborhoodClick,
  flyToNeighborhood,
  onFilterChange
}) => {
  const chicagoCenter = [41.8350, -87.6500];
  const defaultZoom = 10.5;

  const chicagoBounds = [
    [41.64, -87.94],
    [42.02, -87.52]
  ];

  const getRiskColor = (riskLevel) => {
    if (!riskLevel) return '#5DD39E';
    const risk = riskLevel.toLowerCase();
    if (risk.includes('high')) return '#FF6B6B';
    if (risk.includes('medium')) return '#FFB347';
    return '#5DD39E';
  };

  const getRadius = (incidents) => {
    if (!incidents) return 10;
    const minRadius = 10;
    const maxRadius = 30;
    const maxIncidents = 12000;
    const normalized = Math.min(incidents / maxIncidents, 1);
    return minRadius + (normalized * (maxRadius - minRadius));
  };

  const getPolygonCenter = (geometry) => {
    if (!geometry) return null;
    
    let coords;
    if (geometry.type === 'MultiPolygon') {
      coords = geometry.coordinates[0][0];
    } else if (geometry.type === 'Polygon') {
      coords = geometry.coordinates[0];
    } else {
      return null;
    }
    
    const lats = coords.map(c => c[1]);
    const lngs = coords.map(c => c[0]);
    return [
      (Math.min(...lats) + Math.max(...lats)) / 2,
      (Math.min(...lngs) + Math.max(...lngs)) / 2
    ];
  };

  const getFilteredFeatures = useCallback(() => {
    if (!geoJsonData) return [];
    
    return geoJsonData.features.filter(feature => {
      const csvData = feature.properties.csvData;
      if (!csvData) return false;
      
      if (activeFilter === 'all') return true;
      
      const riskLevel = csvData.final_risk?.toLowerCase() || '';
      if (activeFilter === 'high') return riskLevel.includes('high');
      if (activeFilter === 'medium') return riskLevel.includes('medium');
      if (activeFilter === 'low') return riskLevel.includes('low');
      
      return true;
    });
  }, [geoJsonData, activeFilter]);

  const flyTo = flyToNeighborhood ? {
    center: flyToNeighborhood.center,
    zoom: 12
  } : null;

  // FIXED: Direct click handler that calls the parent callback
  const handleCircleClick = (csvData) => {
    console.log('Circle clicked:', csvData.neighborhood);
    onNeighborhoodClick(csvData);
  };

  const filters = [
    { key: 'all', label: 'All Areas' },
    { key: 'high', label: 'High Activity' },
    { key: 'medium', label: 'Moderate' },
    { key: 'low', label: 'Lower' }
  ];

  return (
    <>
      {/* Filter Tabs */}
      <div className="filter-tabs" data-testid="filter-tabs">
        {filters.map(filter => (
          <button
            key={filter.key}
            className={`filter-tab ${activeFilter === filter.key ? 'active' : ''}`}
            onClick={() => onFilterChange(filter.key)}
            data-testid={`filter-${filter.key}`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <MapContainer
        center={chicagoCenter}
        zoom={defaultZoom}
        className="map-container"
        zoomControl={true}
        maxBounds={chicagoBounds}
        maxBoundsViscosity={0.9}
        minZoom={10}
        data-testid="chicago-map"
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {getFilteredFeatures().map((feature, idx) => {
          const csvData = feature.properties.csvData;
          const center = getPolygonCenter(feature.geometry);
          
          if (!center || !csvData) return null;
          
          const color = getRiskColor(csvData.final_risk);
          const radius = getRadius(csvData.crime_total_incidents);
          const isSelected = selectedNeighborhood?.neighborhood === csvData.neighborhood;
          
          return (
            <CircleMarker
              key={`circle-${csvData.neighborhood}-${idx}`}
              center={center}
              radius={radius}
              pathOptions={{
                fillColor: color,
                fillOpacity: isSelected ? 0.95 : 0.65,
                color: isSelected ? '#ffffff' : color,
                weight: isSelected ? 3 : 1.5,
                opacity: 1
              }}
              eventHandlers={{
                click: () => handleCircleClick(csvData),
                mouseover: (e) => {
                  e.target.setStyle({ fillOpacity: 0.9, weight: 2.5 });
                  onNeighborhoodHover(csvData, { 
                    x: e.originalEvent?.pageX || 0, 
                    y: e.originalEvent?.pageY || 0 
                  });
                },
                mouseout: (e) => {
                  e.target.setStyle({ 
                    fillOpacity: isSelected ? 0.95 : 0.65, 
                    weight: isSelected ? 3 : 1.5 
                  });
                  onNeighborhoodHover(null, null);
                }
              }}
              data-testid={`circle-${csvData.neighborhood}`}
            >
              <Tooltip direction="top" offset={[0, -radius]} opacity={0.95}>
                <strong>{csvData.neighborhood}</strong>
              </Tooltip>
            </CircleMarker>
          );
        })}
        
        <MapController flyTo={flyTo} />
      </MapContainer>
    </>
  );
};

export default ChicagoMap;


