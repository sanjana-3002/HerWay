import React from 'react';

const Legend = () => {
  return (
    <div className="legend" data-testid="legend">
      <div className="legend-title">HerWay Chicago</div>
      <div className="legend-subtitle">Community Awareness Guide</div>
      
      <div className="legend-items">
        <div className="legend-item" data-testid="legend-high">
          <div className="legend-dot high"></div>
          <span>Higher Activity</span>
        </div>
        <div className="legend-item" data-testid="legend-medium">
          <div className="legend-dot medium"></div>
          <span>Moderate Activity</span>
        </div>
        <div className="legend-item" data-testid="legend-low">
          <div className="legend-dot low"></div>
          <span>Lower Activity</span>
        </div>
      </div>

      <div className="legend-footer">
        Circle size = incident volume<br/>
        Hover to preview<br/>
        Click for full analysis
      </div>
    </div>
  );
};

export default Legend;