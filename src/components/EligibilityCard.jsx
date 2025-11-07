import React, { useState } from 'react';
import { MapPin, Star, Briefcase, DollarSign, ChevronDown, ChevronUp, CheckCircle, AlertCircle, TrendingUp, Brain, Award, Target, Activity } from 'lucide-react';
import './EligibilityCard.css';

const EligibilityCard = ({ college }) => {
  const [showBranches, setShowBranches] = useState(false);

  const getProbabilityIcon = (probability) => {
    if (probability === 'Highly Safe') return <CheckCircle size={18} className="probability-icon highly-safe" />;
    if (probability === 'Safe') return <CheckCircle size={18} className="probability-icon safe" />;
    if (probability === 'Probable') return <Activity size={18} className="probability-icon probable" />;
    if (probability === 'Moderate') return <AlertCircle size={18} className="probability-icon moderate" />;
    if (probability === 'Reach') return <TrendingUp size={18} className="probability-icon reach" />;
    return null;
  };

  const getProbabilityClass = (probability) => {
    return `probability-badge ${probability.toLowerCase().replace(/\s+/g, '-')}`;
  };

  const formatPackage = (pkg) => {
    if (!pkg) return 'N/A';
    const lakh = pkg / 100000;
    return `₹${lakh.toFixed(1)}L`;
  };

  const formatFee = (fee) => {
    if (!fee) return 'N/A';
    return `₹${fee.toLocaleString('en-IN')}`;
  };

  const getRecommendationLevel = (score) => {
    if (score >= 85) return { label: 'Highly Recommended', color: '#10b981', emoji: '🌟' };
    if (score >= 70) return { label: 'Recommended', color: '#3b82f6', emoji: '✨' };
    if (score >= 55) return { label: 'Worth Considering', color: '#f59e0b', emoji: '💡' };
    return { label: 'Consider Carefully', color: '#ef4444', emoji: '⚠️' };
  };

  const recommendation = college.recommendation_score ? getRecommendationLevel(college.recommendation_score) : null;

  return (
    <div className={`eligibility-card ${college.probability.toLowerCase().replace(/\s+/g, '-')}`}>
      {/* Header with ML Recommendation Score */}
      <div className="eligibility-card-header">
        <div className="eligibility-card-title">
          <h3>{college.name}</h3>
          <div className={getProbabilityClass(college.probability)}>
            {getProbabilityIcon(college.probability)}
            {college.probability}
          </div>
        </div>

        {/* ML Recommendation Badge */}
        {recommendation && (
          <div className="ml-recommendation-badge" style={{ borderColor: recommendation.color }}>
            <Brain size={16} style={{ color: recommendation.color }} />
            <span style={{ color: recommendation.color }}>
              {recommendation.emoji} AI Score: {college.recommendation_score.toFixed(1)}/100
            </span>
            <span className="recommendation-label" style={{ background: recommendation.color }}>
              {recommendation.label}
            </span>
          </div>
        )}
      </div>

      {/* College Info */}
      <div className="eligibility-card-info">
        <div className="info-item">
          <MapPin size={16} />
          <span>{college.location}</span>
        </div>

        {college.rating && (
          <div className="info-item">
            <Star size={16} className="star-icon" />
            <span>{college.rating}/5.0</span>
          </div>
        )}

        {college.average_package && (
          <div className="info-item">
            <Briefcase size={16} />
            <span>Avg: {formatPackage(college.average_package)}</span>
            {college.highest_package && (
              <span className="highest-text">
                | Highest: {formatPackage(college.highest_package)}
              </span>
            )}
          </div>
        )}
      </div>

      {/* ML Score Breakdown - Simplified */}
      {college.score_breakdown && showBranches && (
        <div className="ml-score-breakdown-compact">
          <div className="breakdown-compact-title">
            <Award size={14} />
            <span>AI Factors</span>
          </div>
          <div className="breakdown-chips">
            {Object.entries(college.score_breakdown)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 3)
              .map(([key, value]) => (
                <div key={key} className="factor-chip" style={{
                  background: value >= 80 ? '#d1fae5' : value >= 60 ? '#dbeafe' : '#fef3c7',
                  color: value >= 80 ? '#047857' : value >= 60 ? '#1e40af' : '#d97706'
                }}>
                  <span className="factor-name">{key.replace(/_/g, ' ')}</span>
                  <span className="factor-score">{value.toFixed(0)}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Branches Summary */}
      <div className="eligible-branches-summary">
        <strong>{college.eligible_branches.length}</strong> Eligible Branch{college.eligible_branches.length !== 1 ? 'es' : ''}
        <button
          className="toggle-branches-btn"
          onClick={() => setShowBranches(!showBranches)}
        >
          {showBranches ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          {showBranches ? 'Hide' : 'Show'} Details
        </button>
      </div>

      {/* Branch Details with ML Predictions */}
      {showBranches && (
        <div className="branches-list">
          {college.eligible_branches.map((branch, idx) => (
            <div key={idx} className="branch-item">
              <div className="branch-item-header">
                <div className="branch-name">{branch.name}</div>
                <div className={getProbabilityClass(branch.probability)}>
                  {getProbabilityIcon(branch.probability)}
                  {branch.probability}
                </div>
              </div>

              {/* ML Probability Percentage */}
              {branch.probability_percentage !== undefined && (
                <div className="ml-probability-bar">
                  <div className="probability-bar-container">
                    <div
                      className="probability-bar-fill"
                      style={{
                        width: `${branch.probability_percentage}%`,
                        background: branch.color || '#3b82f6'
                      }}
                    >
                      <span className="probability-percentage">{branch.probability_percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                  <span className="probability-label">ML Admission Probability</span>
                </div>
              )}

              {/* Branch Details */}
              <div className="branch-details">
                <div className="branch-detail">
                  <span className="detail-label">Your Rank:</span>
                  <span className="detail-value rank-value">{branch.your_rank.toLocaleString('en-IN')}</span>
                </div>
                <div className="branch-detail">
                  <span className="detail-label">2024 Cutoff:</span>
                  <span className="detail-value">{branch.cutoff_rank.toLocaleString('en-IN')}</span>
                </div>
                <div className="branch-detail">
                  <span className="detail-label">Difference:</span>
                  <span className="detail-value positive">+{branch.rank_difference.toLocaleString('en-IN')}</span>
                </div>

                {/* ML Forecast for 2025 */}
                {branch.forecast_2025 && (
                  <div className="branch-detail forecast">
                    <Target size={14} className="forecast-icon" />
                    <span className="detail-label">2025 Forecast:</span>
                    <span className="detail-value forecast-value">{branch.forecast_2025.toLocaleString('en-IN')}</span>
                  </div>
                )}

                {/* Trend Indicator */}
                {branch.trend && branch.trend !== 'Unknown' && (
                  <div className="branch-detail trend">
                    <TrendingUp size={14} />
                    <span className="detail-label">Trend:</span>
                    <span className={`detail-value trend-${branch.trend.toLowerCase().replace(/\s+/g, '-')}`}>
                      {branch.trend}
                    </span>
                  </div>
                )}

                {branch.annual_fee && (
                  <div className="branch-detail">
                    <DollarSign size={14} />
                    <span className="detail-label">Annual Fee:</span>
                    <span className="detail-value">{formatFee(branch.annual_fee)}</span>
                  </div>
                )}
              </div>

              {/* ML Confidence Factors - Simplified */}
              {branch.ml_confidence && (
                <div className="ml-confidence-compact">
                  {Object.entries(branch.ml_confidence).map(([key, value]) => (
                    <span key={key} className="confidence-tag">
                      {key.replace(/_/g, ' ')}: {value}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EligibilityCard;
