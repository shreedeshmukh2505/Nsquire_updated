import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './CollegeSelector.css';
import { API_BASE_URL } from '../config';

const CollegeSelector = ({ allColleges, selectedColleges, onCollegeSelect, onRemoveCollege }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredColleges, setFilteredColleges] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchRef = useRef(null);

  // Filter colleges based on search query
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredColleges([]);
      setShowDropdown(false);
      return;
    }

    const filtered = allColleges.filter(college =>
      college.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !selectedColleges.find(sc => sc.id === college.id)
    );

    setFilteredColleges(filtered);
    setShowDropdown(filtered.length > 0);
  }, [searchQuery, allColleges, selectedColleges]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectCollege = (college) => {
    onCollegeSelect(college);
    setSearchQuery('');
    setShowDropdown(false);
  };

  return (
    <div className="college-selector">
      {/* Search Input */}
      <div className="search-container" ref={searchRef}>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search colleges by name (e.g., VJTI, COEP, VIT)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery && setShowDropdown(true)}
          />
          {searchQuery && (
            <button
              className="clear-search-btn"
              onClick={() => {
                setSearchQuery('');
                setShowDropdown(false);
              }}
            >
              ✕
            </button>
          )}
        </div>

        {/* Dropdown Results */}
        {showDropdown && (
          <div className="search-dropdown">
            {filteredColleges.length > 0 ? (
              <>
                {filteredColleges.slice(0, 10).map((college) => (
                  <div
                    key={college.id}
                    className="dropdown-item"
                    onClick={() => handleSelectCollege(college)}
                  >
                    <div className="college-info">
                      <span className="college-name">{college.name}</span>
                      <span className="college-meta">
                        <span className="location">📍 {college.location}</span>
                        <span className="rating">⭐ {college.rating.toFixed(1)}</span>
                      </span>
                    </div>
                    <span className="add-icon">+</span>
                  </div>
                ))}
                {filteredColleges.length > 10 && (
                  <div className="dropdown-footer">
                    Showing 10 of {filteredColleges.length} results
                  </div>
                )}
              </>
            ) : (
              <div className="dropdown-empty">
                No colleges found matching "{searchQuery}"
              </div>
            )}
          </div>
        )}
      </div>

      {/* Selected Colleges */}
      {selectedColleges.length > 0 && (
        <div className="selected-colleges">
          <h3 className="selected-title">
            Selected Colleges ({selectedColleges.length}/4)
          </h3>
          <div className="selected-chips">
            {selectedColleges.map((college) => (
              <div key={college.id} className="college-chip">
                <div className="chip-content">
                  <span className="chip-name">{college.name}</span>
                  <span className="chip-location">{college.location}</span>
                </div>
                <button
                  className="chip-remove"
                  onClick={() => onRemoveCollege(college.id)}
                  title="Remove college"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CollegeSelector;
