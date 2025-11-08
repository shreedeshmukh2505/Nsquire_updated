import React, { useState } from 'react';
import axios from 'axios';
import CategorySelector from './CategorySelector';
import RankSlider from './RankSlider';
import EligibilityCard from './EligibilityCard';
import { Target, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import './RankPredictor.css';
import { API_BASE_URL } from '../config';

const RankPredictor = () => {
  const [rank, setRank] = useState(10000);
  const [category, setCategory] = useState('GOPEN');
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    if (!rank || rank < 1 || rank > 100000) {
      setError('Please enter a valid rank between 1 and 100,000');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/predict`, {
        rank: rank,
        category: category
      });

      setPredictions(response.data);
    } catch (err) {
      console.error('Error predicting colleges:', err);
      setError(err.response?.data?.error || 'Failed to predict colleges. Please try again.');
      setPredictions(null);
    } finally {
      setLoading(false);
    }
  };

  const getSummaryStats = () => {
    if (!predictions || !predictions.eligible_colleges) return null;

    const safe = predictions.eligible_colleges.filter(c => c.probability === 'Safe').length;
    const moderate = predictions.eligible_colleges.filter(c => c.probability === 'Moderate').length;
    const reach = predictions.eligible_colleges.filter(c => c.probability === 'Reach').length;

    return { safe, moderate, reach };
  };

  const stats = getSummaryStats();

  return (
    <div className="rank-predictor">
      <div className="rank-predictor-container">
        <div className="rank-predictor-header">
          <Target size={36} className="header-icon" />
          <h1>College Predictor</h1>
          <p>Find out which colleges you're eligible for based on your MHT-CET rank</p>
        </div>

        <CategorySelector
          selectedCategory={category}
          onCategoryChange={setCategory}
        />

        <RankSlider
          rank={rank}
          onRankChange={setRank}
        />

        <div className="predict-button-container">
          <button
            className="predict-button"
            onClick={handlePredict}
            disabled={loading || !rank}
          >
            {loading ? 'Predicting...' : 'Predict Eligible Colleges'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing cutoff data for {category} category...</p>
          </div>
        )}

        {!loading && predictions && predictions.eligible_colleges && (
          <div className="predictions-results">
            <div className="results-header">
              <h2>Your Eligibility Results</h2>
              <div className="results-summary">
                <div className="summary-item">
                  <span className="summary-label">Rank:</span>
                  <span className="summary-value">{predictions.rank.toLocaleString('en-IN')}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Category:</span>
                  <span className="summary-value">{predictions.category}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Eligible Colleges:</span>
                  <span className="summary-value">{predictions.total_colleges}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Branches:</span>
                  <span className="summary-value">{predictions.total_branches}</span>
                </div>
              </div>
            </div>

            {stats && (
              <div className="probability-stats">
                <div className="stat-card safe">
                  <CheckCircle size={24} />
                  <div className="stat-value">{stats.safe}</div>
                  <div className="stat-label">Safe Colleges</div>
                </div>
                <div className="stat-card moderate">
                  <AlertCircle size={24} />
                  <div className="stat-value">{stats.moderate}</div>
                  <div className="stat-label">Moderate Colleges</div>
                </div>
                <div className="stat-card reach">
                  <TrendingUp size={24} />
                  <div className="stat-value">{stats.reach}</div>
                  <div className="stat-label">Reach Colleges</div>
                </div>
              </div>
            )}

            {predictions.eligible_colleges.length === 0 ? (
              <div className="no-results">
                <AlertCircle size={48} />
                <h3>No Eligible Colleges Found</h3>
                <p>Unfortunately, no colleges match your rank and category combination. Try:</p>
                <ul>
                  <li>Improving your rank through additional attempts</li>
                  <li>Exploring different admission categories</li>
                  <li>Considering management quota options</li>
                </ul>
              </div>
            ) : (
              <div className="eligible-colleges-list">
                {predictions.eligible_colleges.map((college, idx) => (
                  <EligibilityCard key={college.id || idx} college={college} />
                ))}
              </div>
            )}
          </div>
        )}

        {!loading && !predictions && !error && (
          <div className="instructions-card">
            <Target size={48} className="instructions-icon" />
            <h3>How to Use the College Predictor</h3>
            <ol>
              <li><strong>Select your category</strong> from the options above (GOPEN or LOPEN)</li>
              <li><strong>Enter your MHT-CET rank</strong> using the slider or input box</li>
              <li><strong>Click "Predict"</strong> to see which colleges you're eligible for</li>
              <li><strong>Review the results</strong> with probability indicators:
                <ul>
                  <li><span className="safe-indicator">Safe</span> - You have a strong chance of admission</li>
                  <li><span className="moderate-indicator">Moderate</span> - Decent chance, worth applying</li>
                  <li><span className="reach-indicator">Reach</span> - Lower chance, but possible</li>
                </ul>
              </li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};

export default RankPredictor;
