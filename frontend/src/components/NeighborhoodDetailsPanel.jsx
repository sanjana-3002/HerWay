// HerWay insights panel providing contextual neighborhood analysis from crime records, 311 requests and Reddit discussions
import React from 'react';
import { X, Clock, AlertTriangle, MapPin, Compass } from 'lucide-react';

const NeighborhoodDetailsPanel = ({ data, onClose }) => {
  if (!data) return null;

  const {
    neighborhood,
    final_risk,
    combined_score,
    crime_total_incidents,
    crime_top_types,
    crime_violent_pct,
    crime_night_pct,
    crime_peak_hour,
    crime_peak_day,
    crime_peak_month,
    crime_top_location,
    requests_311_total,
    avg_resolution_hours,
    street_light_complaints,
    most_common_complaint,
    reddit_total_posts,
    reddit_fear_ratio,
    reddit_positive_reassuring,
    reddit_negative_fear,
    reddit_neutral_concern
  } = data;

  const getRiskClass = (risk) => {
    if (!risk) return 'low';
    const r = risk.toLowerCase();
    if (r.includes('high')) return 'high';
    if (r.includes('medium')) return 'medium';
    return 'low';
  };

  const getActivityLabel = (risk) => {
    if (!risk) return 'Lower Activity';
    const r = risk.toLowerCase();
    if (r.includes('high')) return 'Higher Activity';
    if (r.includes('medium')) return 'Moderate Activity';
    return 'Lower Activity';
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return Number(num).toLocaleString();
  };

  const formatPercent = (num) => {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return `${Number(num).toFixed(1)}%`;
  };

  const crimeTypes = crime_top_types ? crime_top_types.split('|').map(t => t.trim()).slice(0, 3) : [];

  const totalSentiment = (reddit_negative_fear || 0) + (reddit_neutral_concern || 0) + (reddit_positive_reassuring || 0);
  const concernPct = totalSentiment > 0 ? ((reddit_negative_fear || 0) / totalSentiment * 100).toFixed(0) : 0;
  const neutralPct = totalSentiment > 0 ? ((reddit_neutral_concern || 0) / totalSentiment * 100).toFixed(0) : 0;
  const positivePct = totalSentiment > 0 ? ((reddit_positive_reassuring || 0) / totalSentiment * 100).toFixed(0) : 0;

  const getSummary = () => {
    const risk = final_risk?.toLowerCase() || '';
    if (risk.includes('high')) {
      return `${neighborhood} has elevated activity levels — increased awareness recommended when visiting.`;
    } else if (risk.includes('medium')) {
      return `${neighborhood} has moderate activity levels — standard urban awareness applies.`;
    }
    return `${neighborhood} has lower activity levels — typical neighborhood with isolated concerns.`;
  };

  const getTips = () => {
    const tips = [];
    if (crime_night_pct > 45) {
      tips.push('Higher proportion of incidents occur at night — consider daytime visits when possible');
    }
    if (crime_violent_pct > 35) {
      tips.push('Some violent incidents reported — traveling with others recommended at night');
    }
    if (street_light_complaints > 500) {
      tips.push('Street lighting issues have been reported in parts of this area');
    }
    if (crime_peak_hour) {
      tips.push(`Peak activity around ${crime_peak_hour} — plan accordingly`);
    }
    if (tips.length === 0) {
      tips.push('Standard urban awareness is recommended');
    }
    return tips;
  };

  return (
    <div className="details-panel" data-testid="details-panel">
      {/* Mobile drag handle */}
      <div className="details-drag-handle" onClick={onClose}>
      <div className="drag-indicator"></div>
    </div>
      <div className="details-header">
        <div>
          <h2>{neighborhood}</h2>
          <div className="subtitle">
            Score: {combined_score?.toFixed(3) || 'N/A'} · Crime + 311 + Reddit
          </div>
          <span className={`risk-badge ${getRiskClass(final_risk)}`}>
            {getActivityLabel(final_risk)}
          </span>
        </div>
        <button className="details-close" onClick={onClose} data-testid="details-close">
          <X size={18} />
        </button>
      </div>

      <div className="details-content">
        <div className="details-summary">
          {getSummary()}
        </div>

        <div className="details-section">
          <div className="section-title">
            <AlertTriangle size={14} />
            INCIDENT DATA
          </div>
          
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-value">{formatNumber(crime_total_incidents)}</div>
              <div className="stat-label">INCIDENTS</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{formatPercent(crime_violent_pct)}</div>
              <div className="stat-label">VIOLENT</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{formatPercent(crime_night_pct)}</div>
              <div className="stat-label">AT NIGHT</div>
            </div>
          </div>

          {crimeTypes.length > 0 && (
            <div className="crime-types">
              {crimeTypes.map((type, i) => (
                <span key={i} className="crime-type-tag">{type}</span>
              ))}
            </div>
          )}

          <div className="peak-time-box">
            <Clock size={16} />
            <span className="peak-time-text">
              Peaks {crime_peak_hour || 'N/A'} · {crime_peak_day || 'N/A'}s
            </span>
          </div>
        </div>

        <div className="details-section">
          <div className="section-title">
            <MapPin size={14} />
            311 SERVICE REQUESTS
          </div>
          
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-value">{formatNumber(requests_311_total)}</div>
              <div className="stat-label">REQUESTS</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{formatNumber(street_light_complaints)}</div>
              <div className="stat-label">LIGHT OUTAGES</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{Math.round(avg_resolution_hours || 0)}h</div>
              <div className="stat-label">AVG FIX TIME</div>
            </div>
          </div>

          <div className="info-row">
            <span className="info-label">Most common</span>
            <span className="info-value">{most_common_complaint || 'N/A'}</span>
          </div>
        </div>

        <div className="details-section">
          <div className="section-title">
            COMMUNITY VOICE (REDDIT)
          </div>
          
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-value">{formatNumber(reddit_total_posts)}</div>
              <div className="stat-label">POSTS</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{formatPercent((reddit_fear_ratio || 0) * 100)}</div>
              <div className="stat-label">CONCERNED</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{formatNumber(reddit_positive_reassuring)}</div>
              <div className="stat-label">POSITIVE</div>
            </div>
          </div>

          <div className="sentiment-bar-container">
            <div className="sentiment-bar">
              <div className="sentiment-segment fear" style={{ width: `${concernPct}%` }} />
              <div className="sentiment-segment neutral" style={{ width: `${neutralPct}%` }} />
              <div className="sentiment-segment positive" style={{ width: `${positivePct}%` }} />
            </div>
            <div className="sentiment-labels">
              <span>Concerned {concernPct}%</span>
              <span>Neutral {neutralPct}%</span>
              <span>Positive {positivePct}%</span>
            </div>
          </div>
        </div>

        <div className="details-section">
          <div className="section-title">
            <Compass size={14} />
            VISITOR TIPS
          </div>

          <div className="safety-tips">
            {getTips().map((tip, i) => (
              <div key={i} className="safety-tip">{tip}</div>
            ))}
          </div>

          <div className="time-boxes">
            <div className="time-box">
              <div className="time-box-label safer">QUIETER TIMES</div>
              <div className="time-box-value">Daytime hours, especially weekday mornings</div>
            </div>
            <div className="time-box">
              <div className="time-box-label risk">BUSIER TIMES</div>
              <div className="time-box-value">
                {crime_peak_hour || 'N/A'} · {crime_peak_day || 'N/A'}s · especially in {crime_peak_month || 'N/A'}
              </div>
            </div>
          </div>
        </div>

        <div className="source-note">
          Data combined from public records, 311 requests, and Reddit community discussions
        </div>
      </div>
    </div>
  );
};

export default NeighborhoodDetailsPanel;