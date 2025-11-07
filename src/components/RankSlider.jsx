import React from 'react';
import { TrendingUp } from 'lucide-react';
import './RankSlider.css';

const RankSlider = ({ rank, onRankChange }) => {
  const handleSliderChange = (e) => {
    onRankChange(parseInt(e.target.value));
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    if (value === '') {
      onRankChange('');
      return;
    }

    const numValue = parseInt(value);
    if (!isNaN(numValue) && numValue >= 1 && numValue <= 100000) {
      onRankChange(numValue);
    }
  };

  const formatRank = (rank) => {
    if (!rank) return '0';
    return rank.toLocaleString('en-IN');
  };

  // Calculate slider percentage for background gradient
  const sliderPercentage = ((rank || 0) / 100000) * 100;

  return (
    <div className="rank-slider">
      <div className="rank-slider-header">
        <TrendingUp size={20} />
        <h3>Enter Your CET Rank</h3>
      </div>
      <p className="rank-slider-description">
        Use the slider or input box to enter your MHT-CET rank (1 - 100,000)
      </p>

      <div className="rank-display">
        <div className="rank-display-value">{formatRank(rank || 0)}</div>
        <div className="rank-display-label">Your Rank</div>
      </div>

      <div className="slider-container">
        <input
          type="range"
          min="1"
          max="100000"
          value={rank || 1}
          onChange={handleSliderChange}
          className="rank-range-slider"
          style={{
            background: `linear-gradient(to right, #667eea 0%, #764ba2 ${sliderPercentage}%, #e5e7eb ${sliderPercentage}%, #e5e7eb 100%)`
          }}
        />
        <div className="slider-labels">
          <span>1</span>
          <span>25,000</span>
          <span>50,000</span>
          <span>75,000</span>
          <span>100,000</span>
        </div>
      </div>

      <div className="rank-input-container">
        <label htmlFor="rank-input">Or enter exact rank:</label>
        <input
          id="rank-input"
          type="number"
          min="1"
          max="100000"
          value={rank || ''}
          onChange={handleInputChange}
          placeholder="Enter rank..."
          className="rank-input"
        />
      </div>
    </div>
  );
};

export default RankSlider;
