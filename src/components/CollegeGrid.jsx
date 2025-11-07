import React from 'react';
import { MapPin, Star, DollarSign, Briefcase, GraduationCap, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './CollegeGrid.css';

const CollegeGrid = ({ colleges, loading, error }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="college-grid-loading">
        <div className="loading-spinner"></div>
        <p>Searching colleges...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="college-grid-error">
        <p>{error}</p>
      </div>
    );
  }

  if (!colleges || colleges.length === 0) {
    return (
      <div className="college-grid-empty">
        <GraduationCap size={64} className="empty-icon" />
        <h3>No colleges found</h3>
        <p>Try adjusting your filters or search query</p>
      </div>
    );
  }

  const formatFee = (fee) => {
    if (!fee) return 'N/A';
    return `₹${fee.toLocaleString('en-IN')}`;
  };

  const formatPackage = (pkg) => {
    if (!pkg) return 'N/A';
    const lakh = pkg / 100000;
    return `₹${lakh.toFixed(1)}L`;
  };

  return (
    <div className="college-grid">
      <div className="college-grid-header">
        <h3>Found {colleges.length} college{colleges.length !== 1 ? 's' : ''}</h3>
      </div>

      <div className="college-cards">
        {colleges.map((college) => (
          <div key={college.id} className="college-card">
            <div className="college-card-header">
              <h3 className="college-name">{college.name}</h3>
              <span className={`college-type ${college.type?.toLowerCase()}`}>
                {college.type || 'Public'}
              </span>
            </div>

            <div className="college-info">
              <div className="info-row">
                <MapPin size={16} className="info-icon" />
                <span>{college.location || 'Unknown'}</span>
              </div>

              {college.rating && (
                <div className="info-row">
                  <Star size={16} className="info-icon star-icon" />
                  <span className="rating-value">{college.rating}/5.0</span>
                </div>
              )}

              {college.fee_range && (
                <div className="info-row">
                  <DollarSign size={16} className="info-icon" />
                  <span>
                    {college.fee_range.min === college.fee_range.max
                      ? formatFee(college.fee_range.min)
                      : `${formatFee(college.fee_range.min)} - ${formatFee(college.fee_range.max)}`}
                  </span>
                </div>
              )}

              {college.placements?.average && (
                <div className="info-row">
                  <Briefcase size={16} className="info-icon" />
                  <span>Avg: {formatPackage(college.placements.average)}</span>
                  {college.placements.highest && (
                    <span className="highest-package">
                      | Highest: {formatPackage(college.placements.highest)}
                    </span>
                  )}
                </div>
              )}

              {college.branch_count && (
                <div className="info-row">
                  <GraduationCap size={16} className="info-icon" />
                  <span>{college.branch_count} Branch{college.branch_count !== 1 ? 'es' : ''}</span>
                </div>
              )}
            </div>

            {college.top_branches && college.top_branches.length > 0 && (
              <div className="top-branches">
                <strong>Top Branches:</strong>
                <div className="branch-tags">
                  {college.top_branches.slice(0, 3).map((branch, idx) => (
                    <span key={idx} className="branch-tag">{branch}</span>
                  ))}
                  {college.top_branches.length > 3 && (
                    <span className="branch-tag more">+{college.top_branches.length - 3} more</span>
                  )}
                </div>
              </div>
            )}

            {college.facilities_count > 0 && (
              <div className="facilities-info">
                {college.facilities_count} Facilities Available
              </div>
            )}

            <div className="college-card-actions">
              <button
                className="view-details-btn"
                onClick={() => {
                  // Navigate to chat with college pre-filled
                  navigate('/chat', { state: { initialMessage: `Tell me about ${college.name}` } });
                }}
              >
                View Details
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CollegeGrid;
