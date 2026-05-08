import React from 'react';
import { formatNumber } from '../utils/dataLoader';

const NeighborhoodTooltip = ({ data, position }) => {
  if (!data || !position) return null;

  const { 
    neighborhood,
    final_risk,
    crime_total_incidents,
    crime_top_types,
    crime_peak_hour,
    crime_peak_day,
    requests_311_total,
    most_common_complaint
  } = data;

  const formatCrimeTypes = (types) => {
    if (!types) return 'N/A';
    return types.split('|').slice(0, 2).map(t => t.trim()).join(', ');
  };

  const getActivityLabel = (risk) => {
    if (!risk) return 'Lower Activity';
    const r = risk.toLowerCase();
    if (r.includes('high')) return 'Higher Activity';
    if (r.includes('medium')) return 'Moderate';
    return 'Lower Activity';
  };

  const getActivityClass = (risk) => {
    if (!risk) return 'low';
    const r = risk.toLowerCase();
    if (r.includes('high')) return 'high';
    if (r.includes('medium')) return 'medium';
    return 'low';
  };

  // Position tooltip smartly to avoid edge overflow
  // If near top, show below cursor; if near right edge, shift left
  const showBelow = position.y < 280;
  const showLeft = position.x > window.innerWidth - 180;
  
  const tooltipStyle = {
    left: showLeft ? position.x - 140 : position.x,
    top: showBelow ? position.y + 20 : position.y - 10,
    transform: showBelow 
      ? 'translate(-50%, 0)' 
      : 'translate(-50%, -100%)'
  };

  return (
    <div 
      className="hover-tooltip"
      style={tooltipStyle}
      data-testid="neighborhood-tooltip"
    >
      {/* Header with name + badge */}
      <div className="tooltip-header">
        <div className="tooltip-name">{neighborhood}</div>
        <span className={`tooltip-badge ${getActivityClass(final_risk)}`}>
          {getActivityLabel(final_risk)}
        </span>
      </div>

      {/* Quick Stats Row */}
      <div className="tooltip-quick-stats">
        <div className="tooltip-stat-item">
          <span className="stat-number">{formatNumber(crime_total_incidents)}</span>
          <span className="stat-label">incidents/yr</span>
        </div>
        <div className="tooltip-stat-divider"></div>
        <div className="tooltip-stat-item">
          <span className="stat-number">{formatNumber(requests_311_total)}</span>
          <span className="stat-label">311 requests</span>
        </div>
      </div>

      {/* Details */}
      <div className="tooltip-details">
        <div className="tooltip-row">
          <span className="tooltip-label">Common issues</span>
          <span className="tooltip-value">{formatCrimeTypes(crime_top_types)}</span>
        </div>
        
        {most_common_complaint && (
          <div className="tooltip-row">
            <span className="tooltip-label">Top 311</span>
            <span className="tooltip-value">{most_common_complaint}</span>
          </div>
        )}
      </div>

      {/* Peak Time Highlight */}
      {crime_peak_hour && (
        <div className="tooltip-peak">
          <span className="peak-icon">⏱</span>
          <span className="peak-text">
            Peak: <strong>{crime_peak_hour}</strong> · {crime_peak_day}s
          </span>
        </div>
      )}

      <div className="tooltip-footer">Click for full details</div>
    </div>
  );
};

export default NeighborhoodTooltip;