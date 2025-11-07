import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CollegeSelector from './CollegeSelector';
import ComparisonTable from './ComparisonTable';
import './ComparisonTool.css';

const API_BASE_URL = 'http://localhost:5001';

const ComparisonTool = () => {
  const [selectedColleges, setSelectedColleges] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [allColleges, setAllColleges] = useState([]);

  // Fetch all colleges on component mount
  useEffect(() => {
    fetchAllColleges();
  }, []);

  const fetchAllColleges = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/colleges/all`);
      setAllColleges(response.data);
    } catch (err) {
      console.error('Error fetching colleges:', err);
      setError('Failed to load colleges list');
    }
  };

  const handleCollegeSelect = (college) => {
    if (selectedColleges.find(c => c.id === college.id)) {
      // Already selected, remove it
      setSelectedColleges(selectedColleges.filter(c => c.id !== college.id));
    } else if (selectedColleges.length < 4) {
      // Add to selection (max 4)
      setSelectedColleges([...selectedColleges, college]);
    } else {
      setError('Maximum 4 colleges can be compared at once');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleRemoveCollege = (collegeId) => {
    setSelectedColleges(selectedColleges.filter(c => c.id !== collegeId));
    if (comparisonData) {
      setComparisonData(comparisonData.filter(c => c.id !== collegeId));
    }
  };

  const handleCompare = async () => {
    if (selectedColleges.length < 2) {
      setError('Please select at least 2 colleges to compare');
      setTimeout(() => setError(null), 3000);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/compare`, {
        college_ids: selectedColleges.map(c => c.id)
      });

      setComparisonData(response.data);
    } catch (err) {
      console.error('Error comparing colleges:', err);
      setError(err.response?.data?.error || 'Failed to compare colleges');
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = () => {
    setSelectedColleges([]);
    setComparisonData(null);
    setError(null);
  };

  return (
    <div className="comparison-tool-container">
      <div className="comparison-header">
        <h1 className="comparison-title">
          <span className="icon">📊</span>
          College Comparison Tool
        </h1>
        <p className="comparison-subtitle">
          Compare up to 4 colleges side-by-side to make an informed decision
        </p>
      </div>

      {/* College Selector Section */}
      <div className="selector-section">
        <CollegeSelector
          allColleges={allColleges}
          selectedColleges={selectedColleges}
          onCollegeSelect={handleCollegeSelect}
          onRemoveCollege={handleRemoveCollege}
        />

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            className="compare-btn"
            onClick={handleCompare}
            disabled={selectedColleges.length < 2 || loading}
          >
            {loading ? 'Comparing...' : `Compare ${selectedColleges.length > 0 ? `(${selectedColleges.length})` : ''}`}
          </button>

          {selectedColleges.length > 0 && (
            <button
              className="clear-btn"
              onClick={handleClearAll}
              disabled={loading}
            >
              Clear All
            </button>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparisonData && comparisonData.length > 0 && (
        <ComparisonTable
          colleges={comparisonData}
          onRemoveCollege={handleRemoveCollege}
        />
      )}

      {/* Instructions */}
      {!comparisonData && selectedColleges.length === 0 && (
        <div className="instructions-card">
          <h3>How to use:</h3>
          <ol>
            <li>Search and select 2-4 colleges you want to compare</li>
            <li>Click "Compare" button to see side-by-side comparison</li>
            <li>View details like fees, cutoffs, placements, and facilities</li>
            <li>Remove colleges or clear all to start over</li>
          </ol>
        </div>
      )}
    </div>
  );
};

export default ComparisonTool;
