import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchFilters from './SearchFilters';
import CollegeGrid from './CollegeGrid';
import FilterChip from './FilterChip';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import './CollegeSearch.css';
import { API_BASE_URL } from '../config';

const CollegeSearch = () => {
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filterOptions, setFilterOptions] = useState(null);
  const [currentFilters, setCurrentFilters] = useState({
    q: '',
    location: [],
    min_fee: '',
    max_fee: '',
    min_rating: '',
    branch: '',
    sort: 'rating'
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  });

  // Fetch filter options on mount
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/filters/options`);
        setFilterOptions(response.data);
      } catch (err) {
        console.error('Error fetching filter options:', err);
      }
    };
    fetchFilterOptions();
  }, []);

  // Fetch colleges when filters change
  useEffect(() => {
    fetchColleges();
  }, [currentFilters, pagination.page]);

  const fetchColleges = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
        sort: currentFilters.sort
      };

      if (currentFilters.q) params.q = currentFilters.q;
      if (currentFilters.location.length > 0) params.location = currentFilters.location.join(',');
      if (currentFilters.min_fee) params.min_fee = currentFilters.min_fee;
      if (currentFilters.max_fee) params.max_fee = currentFilters.max_fee;
      if (currentFilters.min_rating) params.min_rating = currentFilters.min_rating;
      if (currentFilters.branch) params.branch = currentFilters.branch;

      const response = await axios.get(`${API_BASE_URL}/api/colleges/search`, { params });

      setColleges(response.data.results || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || 0,
        total_pages: response.data.total_pages || 0
      }));
    } catch (err) {
      console.error('Error fetching colleges:', err);
      setError('Failed to fetch colleges. Please try again.');
      setColleges([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filters) => {
    setCurrentFilters(filters);
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to page 1 on filter change
  };

  const handleRemoveFilter = (filterType) => {
    setCurrentFilters(prev => {
      const updated = { ...prev };
      if (filterType === 'location') {
        updated.location = [];
      } else if (filterType === 'fee_range') {
        updated.min_fee = '';
        updated.max_fee = '';
      } else {
        updated[filterType] = filterType === 'location' ? [] : '';
      }
      return updated;
    });
  };

  const handleRemoveLocation = (location) => {
    setCurrentFilters(prev => ({
      ...prev,
      location: prev.location.filter(loc => loc !== location)
    }));
  };

  const getActiveFilters = () => {
    const active = [];

    if (currentFilters.q) {
      active.push({ type: 'q', label: 'Search', value: currentFilters.q });
    }

    currentFilters.location.forEach(loc => {
      active.push({ type: 'location', label: 'Location', value: loc, removable: loc });
    });

    if (currentFilters.min_fee || currentFilters.max_fee) {
      const feeText = currentFilters.min_fee && currentFilters.max_fee
        ? `₹${parseInt(currentFilters.min_fee).toLocaleString('en-IN')} - ₹${parseInt(currentFilters.max_fee).toLocaleString('en-IN')}`
        : currentFilters.min_fee
        ? `> ₹${parseInt(currentFilters.min_fee).toLocaleString('en-IN')}`
        : `< ₹${parseInt(currentFilters.max_fee).toLocaleString('en-IN')}`;
      active.push({ type: 'fee_range', label: 'Fee', value: feeText });
    }

    if (currentFilters.min_rating) {
      active.push({ type: 'min_rating', label: 'Rating', value: `≥ ${currentFilters.min_rating}` });
    }

    if (currentFilters.branch) {
      active.push({ type: 'branch', label: 'Branch', value: currentFilters.branch });
    }

    return active;
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      setPagination(prev => ({ ...prev, page: newPage }));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const activeFilters = getActiveFilters();

  return (
    <div className="college-search">
      <div className="college-search-container">
        <div className="college-search-header">
          <h1>Find Your Perfect College</h1>
          <p>Search and filter through {pagination.total || '44'} engineering colleges in Maharashtra</p>
        </div>

        <SearchFilters
          onFilterChange={handleFilterChange}
          filterOptions={filterOptions}
        />

        {activeFilters.length > 0 && (
          <div className="active-filters">
            <h4>Active Filters:</h4>
            <div className="filter-chips">
              {activeFilters.map((filter, idx) => (
                <FilterChip
                  key={`${filter.type}-${idx}`}
                  label={filter.label}
                  value={filter.value}
                  onRemove={() => {
                    if (filter.removable) {
                      handleRemoveLocation(filter.removable);
                    } else {
                      handleRemoveFilter(filter.type);
                    }
                  }}
                />
              ))}
            </div>
          </div>
        )}

        <CollegeGrid
          colleges={colleges}
          loading={loading}
          error={error}
        />

        {!loading && !error && pagination.total_pages > 1 && (
          <div className="pagination">
            <button
              className="pagination-btn"
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
            >
              <ChevronLeft size={20} />
              Previous
            </button>

            <div className="pagination-info">
              Page {pagination.page} of {pagination.total_pages}
              <span className="pagination-total">({pagination.total} total)</span>
            </div>

            <button
              className="pagination-btn"
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.total_pages}
            >
              Next
              <ChevronRight size={20} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CollegeSearch;
