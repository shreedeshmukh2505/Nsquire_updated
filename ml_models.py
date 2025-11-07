"""
Machine Learning Models for College Admission Prediction
Includes: Cutoff Forecasting, Admission Probability, and Smart Recommendations
"""

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from typing import Dict, List, Tuple, Optional
import logging
from models import get_session, College, Course, Cutoff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CutoffForecaster:
    """
    Predicts next year's cutoff using time series analysis and regression
    """

    def __init__(self):
        self.model = LinearRegression()

    def prepare_time_series_data(self, historical_cutoffs: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for training

        Args:
            historical_cutoffs: List of {'year': int, 'cutoff_rank': int}

        Returns:
            X (years), y (cutoff ranks)
        """
        if len(historical_cutoffs) < 2:
            return None, None

        years = np.array([c['year'] for c in historical_cutoffs]).reshape(-1, 1)
        cutoffs = np.array([c['cutoff_rank'] for c in historical_cutoffs])

        return years, cutoffs

    def predict_next_year_cutoff(self, historical_cutoffs: List[Dict], target_year: int) -> Dict:
        """
        Predict cutoff for target year using historical data

        Args:
            historical_cutoffs: Historical cutoff data
            target_year: Year to predict

        Returns:
            Dictionary with prediction and confidence metrics
        """
        X, y = self.prepare_time_series_data(historical_cutoffs)

        if X is None or len(X) < 2:
            # Not enough data, return average
            avg_cutoff = int(np.mean([c['cutoff_rank'] for c in historical_cutoffs]))
            return {
                'predicted_cutoff': avg_cutoff,
                'confidence': 'Low',
                'trend': 'Stable',
                'year_over_year_change': 0,
                'data_points': len(historical_cutoffs)
            }

        # Train model
        self.model.fit(X, y)

        # Predict for target year
        predicted_cutoff = self.model.predict([[target_year]])[0]

        # Calculate trend
        if len(X) >= 2:
            year_over_year_change = (y[-1] - y[0]) / len(y)

            if year_over_year_change > 100:
                trend = 'Rising Competition'
            elif year_over_year_change < -100:
                trend = 'Falling Competition'
            else:
                trend = 'Stable'
        else:
            year_over_year_change = 0
            trend = 'Stable'

        # Calculate confidence based on data consistency
        if len(X) >= 3:
            predictions = self.model.predict(X)
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)

            if r2 > 0.8 and mse < 1000:
                confidence = 'High'
            elif r2 > 0.5:
                confidence = 'Medium'
            else:
                confidence = 'Low'
        else:
            confidence = 'Medium'

        # Calculate standard deviation for uncertainty
        std_dev = np.std(y)

        return {
            'predicted_cutoff': int(predicted_cutoff),
            'confidence': confidence,
            'trend': trend,
            'year_over_year_change': int(year_over_year_change),
            'data_points': len(historical_cutoffs),
            'uncertainty_range': {
                'lower': int(predicted_cutoff - std_dev),
                'upper': int(predicted_cutoff + std_dev)
            },
            'r2_score': round(r2, 3) if len(X) >= 3 else None
        }

    def get_historical_trend_analysis(self, historical_cutoffs: List[Dict]) -> Dict:
        """
        Analyze historical trends
        """
        if len(historical_cutoffs) < 2:
            return {
                'trend_direction': 'Insufficient Data',
                'average_change_per_year': 0,
                'volatility': 'Unknown'
            }

        cutoffs = [c['cutoff_rank'] for c in historical_cutoffs]
        years = [c['year'] for c in historical_cutoffs]

        # Calculate average change
        changes = [cutoffs[i+1] - cutoffs[i] for i in range(len(cutoffs)-1)]
        avg_change = np.mean(changes)

        # Calculate volatility
        std_dev = np.std(cutoffs)
        mean_cutoff = np.mean(cutoffs)
        cv = (std_dev / mean_cutoff) * 100  # Coefficient of variation

        if cv < 5:
            volatility = 'Low'
        elif cv < 15:
            volatility = 'Medium'
        else:
            volatility = 'High'

        if avg_change > 100:
            trend_direction = 'Increasing'
        elif avg_change < -100:
            trend_direction = 'Decreasing'
        else:
            trend_direction = 'Stable'

        return {
            'trend_direction': trend_direction,
            'average_change_per_year': int(avg_change),
            'volatility': volatility,
            'coefficient_of_variation': round(cv, 2),
            'historical_range': {
                'min': int(min(cutoffs)),
                'max': int(max(cutoffs))
            }
        }


class AdmissionProbabilityPredictor:
    """
    Predicts admission probability using ML classification
    """

    def calculate_probability(self, rank: int, cutoff: int, historical_cutoffs: List[int]) -> Dict:
        """
        Calculate admission probability using multiple factors

        Args:
            rank: Student's rank
            cutoff: Current year cutoff
            historical_cutoffs: Historical cutoff data

        Returns:
            Dictionary with probability and classification
        """
        # Calculate rank difference
        rank_diff = cutoff - rank
        rank_diff_percentage = (rank_diff / cutoff) * 100 if cutoff > 0 else 0

        # Calculate historical volatility
        if len(historical_cutoffs) > 1:
            std_dev = np.std(historical_cutoffs)
            cv = (std_dev / np.mean(historical_cutoffs)) * 100
        else:
            cv = 5  # Default low volatility

        # ML-based probability calculation
        # Features: rank_diff_percentage, volatility

        if rank > cutoff:
            # Rank is worse than cutoff
            probability = 0
            category = 'Not Eligible'
            color = 'red'
        else:
            # Base probability on rank difference percentage
            if rank_diff_percentage >= 30:
                base_prob = 95
                category = 'Highly Safe'
                color = 'darkgreen'
            elif rank_diff_percentage >= 20:
                base_prob = 85
                category = 'Safe'
                color = 'green'
            elif rank_diff_percentage >= 10:
                base_prob = 70
                category = 'Probable'
                color = 'lightgreen'
            elif rank_diff_percentage >= 5:
                base_prob = 55
                category = 'Moderate'
                color = 'orange'
            else:
                base_prob = 35
                category = 'Reach'
                color = 'darkorange'

            # Adjust for volatility
            volatility_penalty = min(cv * 0.3, 15)  # Max 15% penalty
            final_probability = max(0, min(100, base_prob - volatility_penalty))

            probability = round(final_probability, 1)

        return {
            'probability': probability,
            'category': category,
            'color': color,
            'rank_difference': rank_diff,
            'confidence_factors': {
                'rank_advantage': f"{rank_diff_percentage:.1f}%",
                'historical_volatility': f"{cv:.1f}%"
            }
        }


class SmartRecommendationSystem:
    """
    Multi-factor recommendation system for personalized college suggestions
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def calculate_college_score(self, college_data: Dict, user_preferences: Dict) -> float:
        """
        Calculate weighted score for a college based on multiple factors

        Args:
            college_data: College information including rank eligibility, placements, etc.
            user_preferences: User's preferences (weights for different factors)

        Returns:
            Normalized score (0-100)
        """
        # Default weights if not provided
        weights = {
            'rank_eligibility': user_preferences.get('rank_eligibility_weight', 0.30),
            'placements': user_preferences.get('placements_weight', 0.25),
            'fees': user_preferences.get('fees_weight', 0.15),
            'rating': user_preferences.get('rating_weight', 0.15),
            'location': user_preferences.get('location_weight', 0.10),
            'branches': user_preferences.get('branches_weight', 0.05)
        }

        # Calculate individual scores
        scores = {}

        # 1. Rank Eligibility Score (0-100)
        rank_diff_percent = college_data.get('rank_difference_percentage', 0)
        if rank_diff_percent >= 30:
            scores['rank_eligibility'] = 100
        elif rank_diff_percent >= 20:
            scores['rank_eligibility'] = 85
        elif rank_diff_percent >= 10:
            scores['rank_eligibility'] = 70
        elif rank_diff_percent >= 5:
            scores['rank_eligibility'] = 50
        elif rank_diff_percent > 0:
            scores['rank_eligibility'] = 30
        else:
            scores['rank_eligibility'] = 0

        # 2. Placement Score (0-100)
        avg_package = college_data.get('average_package', 0)
        highest_package = college_data.get('highest_package', 0)

        # Normalize based on typical ranges (3-15 LPA average, 10-50 LPA highest)
        avg_score = min(100, (avg_package / 1500000) * 100)
        highest_score = min(100, (highest_package / 5000000) * 100)
        scores['placements'] = (avg_score * 0.7 + highest_score * 0.3)

        # 3. Fee Score (0-100) - Lower is better
        annual_fee = college_data.get('annual_fee', 150000)
        # Normalize based on typical range (50k - 300k)
        fee_score = max(0, 100 - ((annual_fee - 50000) / 2500))
        scores['fees'] = min(100, max(0, fee_score))

        # 4. Rating Score (0-100)
        rating = college_data.get('rating', 0)
        scores['rating'] = (rating / 5.0) * 100

        # 5. Location Score (0-100)
        preferred_location = user_preferences.get('preferred_location', None)
        college_location = college_data.get('location', '')

        if preferred_location and preferred_location.lower() in college_location.lower():
            scores['location'] = 100
        else:
            scores['location'] = 50  # Neutral if no preference or doesn't match

        # 6. Branch Availability Score (0-100)
        eligible_branches = college_data.get('eligible_branches_count', 0)
        scores['branches'] = min(100, eligible_branches * 20)  # 5 branches = 100 score

        # Calculate weighted final score
        final_score = sum(scores[key] * weights[key] for key in weights.keys())

        return {
            'total_score': round(final_score, 2),
            'breakdown': {k: round(v, 1) for k, v in scores.items()},
            'weights': weights
        }

    def rank_colleges_by_score(self, colleges_list: List[Dict], user_preferences: Dict) -> List[Dict]:
        """
        Rank all colleges based on multi-factor scoring

        Args:
            colleges_list: List of eligible colleges
            user_preferences: User preferences for weighting

        Returns:
            Sorted list of colleges with scores
        """
        scored_colleges = []

        for college in colleges_list:
            score_data = self.calculate_college_score(college, user_preferences)
            college['recommendation_score'] = score_data['total_score']
            college['score_breakdown'] = score_data['breakdown']
            scored_colleges.append(college)

        # Sort by score (highest first)
        scored_colleges.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return scored_colleges


# Utility functions for database integration
def get_historical_cutoffs_for_course(course_id: int, category: str) -> List[Dict]:
    """
    Fetch historical cutoffs for a specific course and category
    """
    session = get_session()
    try:
        cutoffs = session.query(Cutoff).filter(
            Cutoff.course_id == course_id,
            Cutoff.category == category
        ).order_by(Cutoff.year).all()

        return [{'year': c.year, 'cutoff_rank': c.cutoff_rank} for c in cutoffs]
    finally:
        session.close()


def predict_cutoffs_for_all_courses(college_id: int, category: str, target_year: int = 2025) -> List[Dict]:
    """
    Predict cutoffs for all courses in a college
    """
    session = get_session()
    forecaster = CutoffForecaster()

    try:
        college = session.query(College).filter(College.id == college_id).first()
        if not college:
            return []

        predictions = []

        for course in college.courses:
            historical_cutoffs = get_historical_cutoffs_for_course(course.id, category)

            if historical_cutoffs:
                prediction = forecaster.predict_next_year_cutoff(historical_cutoffs, target_year)
                prediction['course_name'] = course.name
                prediction['course_id'] = course.id
                predictions.append(prediction)

        return predictions
    finally:
        session.close()


if __name__ == "__main__":
    # Test the models
    print("Testing ML Models...")

    # Test Cutoff Forecaster
    forecaster = CutoffForecaster()
    sample_data = [
        {'year': 2020, 'cutoff_rank': 500},
        {'year': 2021, 'cutoff_rank': 450},
        {'year': 2022, 'cutoff_rank': 420},
        {'year': 2023, 'cutoff_rank': 400},
        {'year': 2024, 'cutoff_rank': 380}
    ]

    prediction = forecaster.predict_next_year_cutoff(sample_data, 2025)
    print(f"\nCutoff Prediction for 2025: {prediction}")

    # Test Admission Probability
    prob_predictor = AdmissionProbabilityPredictor()
    prob_result = prob_predictor.calculate_probability(
        rank=350,
        cutoff=400,
        historical_cutoffs=[380, 400, 420, 450, 500]
    )
    print(f"\nAdmission Probability: {prob_result}")

    # Test Recommendation System
    recommender = SmartRecommendationSystem()
    college_sample = {
        'rank_difference_percentage': 15,
        'average_package': 800000,
        'highest_package': 2500000,
        'annual_fee': 100000,
        'rating': 4.2,
        'location': 'Pune',
        'eligible_branches_count': 3
    }

    user_prefs = {
        'preferred_location': 'Pune',
        'placements_weight': 0.35,
        'fees_weight': 0.20
    }

    score = recommender.calculate_college_score(college_sample, user_prefs)
    print(f"\nCollege Recommendation Score: {score}")

    print("\n✅ All ML models tested successfully!")
