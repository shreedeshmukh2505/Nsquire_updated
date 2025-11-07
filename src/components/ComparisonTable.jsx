import React, { useState } from 'react';
import './ComparisonTable.css';

const ComparisonTable = ({ colleges, onRemoveCollege }) => {
  const [expandedBranches, setExpandedBranches] = useState({});

  // Toggle branch expansion
  const toggleBranch = (collegeId) => {
    setExpandedBranches(prev => ({
      ...prev,
      [collegeId]: !prev[collegeId]
    }));
  };

  // Get all unique categories across all colleges
  const getAllCategories = () => {
    const categories = new Set();
    colleges.forEach(college => {
      college.courses.forEach(course => {
        Object.keys(course.cutoffs).forEach(cat => categories.add(cat));
      });
    });
    return Array.from(categories).sort();
  };

  const categories = getAllCategories();

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount) return 'N/A';
    return `₹${(amount / 100000).toFixed(2)}L`;
  };

  // Format rank with commas
  const formatRank = (rank) => {
    if (!rank) return 'N/A';
    return rank.toLocaleString();
  };

  // Get best (lowest) cutoff for a course
  const getBestCutoff = (course) => {
    const cutoffs = Object.values(course.cutoffs);
    return cutoffs.length > 0 ? Math.min(...cutoffs) : null;
  };

  return (
    <div className="comparison-results">
      <div className="results-header">
        <h2>Comparison Results</h2>
        <p className="results-count">Comparing {colleges.length} colleges</p>
      </div>

      <div className="comparison-table-wrapper">
        <table className="comparison-table">
          <thead>
            <tr>
              <th className="row-header">Attribute</th>
              {colleges.map((college) => (
                <th key={college.id} className="college-column">
                  <div className="college-header">
                    <h3 className="college-name">{college.name}</h3>
                    <p className="college-location">📍 {college.location}</p>
                    <button
                      className="remove-college-btn"
                      onClick={() => onRemoveCollege(college.id)}
                      title="Remove from comparison"
                    >
                      Remove
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {/* Basic Info Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>📋 Basic Information</strong>
              </td>
            </tr>

            <tr>
              <td className="row-label">Type</td>
              {colleges.map((college) => (
                <td key={college.id}>{college.type}</td>
              ))}
            </tr>

            <tr>
              <td className="row-label">Rating</td>
              {colleges.map((college) => (
                <td key={college.id}>
                  <span className="rating-badge">
                    ⭐ {college.rating.toFixed(1)}/5.0
                  </span>
                </td>
              ))}
            </tr>

            {/* Fees Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>💰 Fees (Annual)</strong>
              </td>
            </tr>

            <tr>
              <td className="row-label">Typical Fee Range</td>
              {colleges.map((college) => {
                const fees = college.courses.map(c => c.fee).filter(f => f > 0);
                const minFee = Math.min(...fees);
                const maxFee = Math.max(...fees);
                return (
                  <td key={college.id}>
                    {minFee === maxFee
                      ? `₹${(minFee / 1000).toFixed(0)}k`
                      : `₹${(minFee / 1000).toFixed(0)}k - ₹${(maxFee / 1000).toFixed(0)}k`}
                  </td>
                );
              })}
            </tr>

            {/* Placements Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>💼 Placements</strong>
              </td>
            </tr>

            <tr>
              <td className="row-label">Average Package</td>
              {colleges.map((college) => (
                <td key={college.id} className={college.placements.average_package > 0 ? 'highlight' : ''}>
                  {formatCurrency(college.placements.average_package)}
                </td>
              ))}
            </tr>

            <tr>
              <td className="row-label">Highest Package</td>
              {colleges.map((college) => (
                <td key={college.id} className={college.placements.highest_package > 0 ? 'highlight' : ''}>
                  {formatCurrency(college.placements.highest_package)}
                </td>
              ))}
            </tr>

            <tr>
              <td className="row-label">Top Recruiters</td>
              {colleges.map((college) => (
                <td key={college.id}>
                  {college.placements.top_recruiters && college.placements.top_recruiters.length > 0
                    ? college.placements.top_recruiters.slice(0, 3).join(', ')
                    : 'N/A'}
                </td>
              ))}
            </tr>

            {/* Cutoffs Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>📊 Cutoffs 2024 (Best across all branches)</strong>
              </td>
            </tr>

            {categories.map(category => (
              <tr key={category}>
                <td className="row-label">{category}</td>
                {colleges.map((college) => {
                  // Find the best cutoff for this category across all courses
                  const cutoffs = college.courses
                    .map(course => course.cutoffs[category])
                    .filter(c => c !== undefined);

                  const bestCutoff = cutoffs.length > 0 ? Math.min(...cutoffs) : null;

                  return (
                    <td key={college.id} className={bestCutoff ? 'highlight-cutoff' : ''}>
                      {bestCutoff ? formatRank(bestCutoff) : 'N/A'}
                    </td>
                  );
                })}
              </tr>
            ))}

            {/* Branches Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>🎓 Available Branches</strong>
              </td>
            </tr>

            <tr>
              <td className="row-label">Branches Count</td>
              {colleges.map((college) => (
                <td key={college.id}>
                  <span className="branch-count">{college.courses.length} branches</span>
                  <button
                    className="toggle-branches-btn"
                    onClick={() => toggleBranch(college.id)}
                  >
                    {expandedBranches[college.id] ? 'Hide' : 'Show'} Details
                  </button>
                </td>
              ))}
            </tr>

            {/* Expanded Branch Details */}
            {colleges.some(c => expandedBranches[c.id]) && (
              <tr className="branch-details-row">
                <td className="row-label">Branch Details</td>
                {colleges.map((college) => (
                  <td key={college.id} className="branch-details-cell">
                    {expandedBranches[college.id] && (
                      <div className="branches-list">
                        {college.courses.slice(0, 5).map((course, idx) => (
                          <div key={idx} className="branch-item">
                            <div className="branch-name">{course.name}</div>
                            <div className="branch-meta">
                              <span>₹{(course.fee / 1000).toFixed(0)}k/year</span>
                              <span>Best: {formatRank(getBestCutoff(course))}</span>
                            </div>
                          </div>
                        ))}
                        {college.courses.length > 5 && (
                          <div className="more-branches">
                            +{college.courses.length - 5} more branches
                          </div>
                        )}
                      </div>
                    )}
                  </td>
                ))}
              </tr>
            )}

            {/* Facilities Section */}
            <tr className="section-header">
              <td colSpan={colleges.length + 1}>
                <strong>🏢 Facilities</strong>
              </td>
            </tr>

            <tr>
              <td className="row-label">Available Facilities</td>
              {colleges.map((college) => (
                <td key={college.id}>
                  <div className="facilities-list">
                    {college.facilities && college.facilities.length > 0
                      ? college.facilities.map((facility, idx) => (
                          <span key={idx} className="facility-tag">{facility}</span>
                        ))
                      : 'N/A'}
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Export Options */}
      <div className="export-section">
        <p className="export-hint">💡 Tip: Take a screenshot or print this page to save your comparison</p>
      </div>
    </div>
  );
};

export default ComparisonTable;
