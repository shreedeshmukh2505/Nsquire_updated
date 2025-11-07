import React, { useState, useEffect } from 'react';
import { Search, MapPin, DollarSign, Star, BookOpen, SlidersHorizontal } from 'lucide-react';
import './SearchFilters.css';

const SearchFilters = ({ onFilterChange, filterOptions }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [minFee, setMinFee] = useState('');
  const [maxFee, setMaxFee] = useState('');
  const [minRating, setMinRating] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Notify parent component of filter changes
    const filters = {
      q: searchQuery,
      location: selectedLocations,
      min_fee: minFee,
      max_fee: maxFee,
      min_rating: minRating,
      branch: selectedBranch,
      sort: sortBy
    };
    onFilterChange(filters);
  }, [searchQuery, selectedLocations, minFee, maxFee, minRating, selectedBranch, sortBy]);

  const handleLocationToggle = (location) => {
    setSelectedLocations(prev =>
      prev.includes(location)
        ? prev.filter(loc => loc !== location)
        : [...prev, location]
    );
  };

  const clearAllFilters = () => {
    setSearchQuery('');
    setSelectedLocations([]);
    setMinFee('');
    setMaxFee('');
    setMinRating('');
    setSelectedBranch('');
    setSortBy('rating');
  };

  const activeFilterCount = [
    searchQuery,
    ...selectedLocations,
    minFee,
    maxFee,
    minRating,
    selectedBranch
  ].filter(Boolean).length;

  return (
    <div className="search-filters">
      <div className="search-filters-header">
        <h2 className="search-filters-title">
          <SlidersHorizontal size={24} />
          Search Colleges
        </h2>
        {activeFilterCount > 0 && (
          <button className="clear-filters-btn" onClick={clearAllFilters}>
            Clear All ({activeFilterCount})
          </button>
        )}
      </div>

      {/* Search Input */}
      <div className="filter-group">
        <label className="filter-label">
          <Search size={18} />
          Search by Name
        </label>
        <input
          type="text"
          className="filter-input search-input"
          placeholder="e.g., VJTI, COEP, PICT..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Sort By */}
      <div className="filter-group">
        <label className="filter-label">Sort By</label>
        <select
          className="filter-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="rating">Rating (High to Low)</option>
          <option value="name">Name (A to Z)</option>
          <option value="fees">Fees (Low to High)</option>
        </select>
      </div>

      {/* Advanced Filters Toggle */}
      <button
        className="advanced-toggle"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
      </button>

      {showAdvanced && (
        <div className="advanced-filters">
          {/* Location Filter */}
          <div className="filter-group">
            <label className="filter-label">
              <MapPin size={18} />
              Location
            </label>
            <div className="location-chips">
              {filterOptions?.locations?.map((location) => (
                <button
                  key={location}
                  className={`location-chip ${selectedLocations.includes(location) ? 'active' : ''}`}
                  onClick={() => handleLocationToggle(location)}
                >
                  {location}
                </button>
              ))}
            </div>
          </div>

          {/* Fee Range */}
          <div className="filter-group">
            <label className="filter-label">
              <DollarSign size={18} />
              Annual Fee Range
            </label>
            <div className="fee-inputs">
              <input
                type="number"
                className="filter-input fee-input"
                placeholder="Min Fee"
                value={minFee}
                onChange={(e) => setMinFee(e.target.value)}
              />
              <span className="fee-separator">to</span>
              <input
                type="number"
                className="filter-input fee-input"
                placeholder="Max Fee"
                value={maxFee}
                onChange={(e) => setMaxFee(e.target.value)}
              />
            </div>
            {filterOptions?.fee_range && (
              <p className="fee-hint">
                Range: ₹{filterOptions.fee_range.min.toLocaleString('en-IN')} - ₹{filterOptions.fee_range.max.toLocaleString('en-IN')}
              </p>
            )}
          </div>

          {/* Rating Filter */}
          <div className="filter-group">
            <label className="filter-label">
              <Star size={18} />
              Minimum Rating
            </label>
            <input
              type="number"
              className="filter-input"
              placeholder="e.g., 4.0"
              min="0"
              max="5"
              step="0.1"
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
            />
            {filterOptions?.rating_range && (
              <p className="fee-hint">
                Available: {filterOptions.rating_range.min} - {filterOptions.rating_range.max}
              </p>
            )}
          </div>

          {/* Branch Filter */}
          <div className="filter-group">
            <label className="filter-label">
              <BookOpen size={18} />
              Branch
            </label>
            <select
              className="filter-select"
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
            >
              <option value="">All Branches</option>
              {filterOptions?.branches?.map((branch) => (
                <option key={branch} value={branch}>
                  {branch}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchFilters;
