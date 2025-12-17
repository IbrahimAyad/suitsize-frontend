"""
ML-Enhanced SuitSize.ai Algorithm v2.0
Based on Academic Research and Industry Best Practices

Implements:
- SVR and GRNN Machine Learning Models
- Customer Similarity Weighting (3,371 records concept)
- Enhanced Confidence Scoring (Distance-based)
- Edge Case Optimization
- Anthropometric Research Integration
"""

import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
import pickle
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnthropometricValidator:
    """Enhanced anthropometric validation based on academic research"""
    
    @staticmethod
    def validate_measurements(height: float, weight: float, unit: str = 'metric') -> Dict[str, Any]:
        """Comprehensive anthropometric validation"""
        
        # Convert to standard units
        if unit == 'imperial':
            height_cm = height * 2.54
            weight_kg = weight * 0.453592
        else:
            height_cm = height
            weight_kg = weight
        
        # Calculate BMI
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Age estimation (approximate, used for model training)
        age_estimate = AnthropometricValidator._estimate_age(height_cm, weight_kg, bmi)
        
        # Body type classification
        body_type = AnthropometricValidator._classify_body_type(height_cm, weight_kg, bmi)
        
        # Anthropometric percentile analysis
        percentiles = AnthropometricValidator._calculate_percentiles(height_cm, weight_kg, bmi)
        
        return {
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'bmi': bmi,
            'age_estimate': age_estimate,
            'body_type': body_type,
            'percentiles': percentiles,
            'is_valid': True,
            'validation_notes': AnthropometricValidator._get_validation_notes(bmi, height_cm, percentiles)
        }
    
    @staticmethod
    def _estimate_age(height_cm: float, weight_kg: float, bmi: float) -> int:
        """Estimate age based on anthropometric data (for model training)"""
        # Simplified age estimation based on height/weight correlations
        # In real implementation, this would be replaced with actual customer age data
        base_age = 35
        
        # Adjust based on height (taller people often slightly younger in customer data)
        if height_cm > 180:
            base_age -= 3
        elif height_cm < 165:
            base_age += 2
        
        # Adjust based on BMI (higher BMI sometimes correlates with older age)
        if bmi > 28:
            base_age += 5
        elif bmi < 22:
            base_age -= 2
        
        return max(18, min(65, base_age))
    
    @staticmethod
    def _classify_body_type(height_cm: float, weight_kg: float, bmi: float) -> str:
        """Enhanced body type classification based on anthropometric research"""
        
        height_weight_ratio = weight_kg / (height_cm / 100)
        
        # Body type classification logic
        if bmi < 18.5:
            return "Slim"
        elif bmi > 30:
            return "Broad"
        elif height_weight_ratio > 1.1:
            return "Athletic"
        elif height_weight_ratio < 0.85:
            return "Slender"
        elif bmi >= 25 and bmi < 30:
            return "Overweight"
        else:
            return "Regular"
    
    @staticmethod
    def _calculate_percentiles(height_cm: float, weight_kg: float, bmi: float) -> Dict[str, float]:
        """Calculate anthropometric percentiles based on general population data"""
        
        # Simplified percentile calculations (would use actual population data)
        # These are approximate values for demonstration
        
        # Height percentiles (approximate male population data)
        height_percentiles = {
            '5th': 165, '10th': 168, '25th': 173, '50th': 178, 
            '75th': 183, '90th': 188, '95th': 193
        }
        
        # Weight percentiles (approximate male population data)
        weight_percentiles = {
            '5th': 60, '10th': 65, '25th': 72, '50th': 80, 
            '75th': 90, '90th': 105, '95th': 120
        }
        
        # Calculate percentiles
        height_percentile = AnthropometricValidator._calculate_percentile(
            height_cm, list(height_percentiles.values())
        )
        
        weight_percentile = AnthropometricValidator._calculate_percentile(
            weight_kg, list(weight_percentiles.values())
        )
        
        # BMI percentiles
        bmi_percentiles = {
            '5th': 20, '10th': 21, '25th': 23, '50th': 25, 
            '75th': 28, '90th': 32, '95th': 35
        }
        
        bmi_percentile = AnthropometricValidator._calculate_percentile(
            bmi, list(bmi_percentiles.values())
        )
        
        return {
            'height_percentile': height_percentile,
            'weight_percentile': weight_percentile,
            'bmi_percentile': bmi_percentile
        }
    
    @staticmethod
    def _calculate_percentile(value: float, percentile_points: List[float]) -> float:
        """Calculate percentile of a value against reference points"""
        if not percentile_points:
            return 50.0
        
        percentile_points = sorted(percentile_points)
        
        if value <= percentile_points[0]:
            return 0.0
        elif value >= percentile_points[-1]:
            return 100.0
        
        # Find position and interpolate
        for i in range(len(percentile_points) - 1):
            if percentile_points[i] <= value <= percentile_points[i + 1]:
                # Linear interpolation
                lower = percentile_points[i]
                upper = percentile_points[i + 1]
                position = (value - lower) / (upper - lower)
                return i * (100 / (len(percentile_points) - 1)) + position * (100 / (len(percentile_points) - 1))
        
        return 50.0
    
    @staticmethod
    def _get_validation_notes(bmi: float, height_cm: float, percentiles: Dict[str, float]) -> List[str]:
        """Generate validation notes based on anthropometric analysis"""
        notes = []
        
        # BMI warnings
        if bmi < 18.5:
            notes.append("BMI indicates underweight - slim fit recommended")
        elif bmi > 30:
            notes.append("BMI indicates overweight - relaxed fit recommended")
        elif bmi > 28:
            notes.append("BMI slightly high - consider relaxed fit for comfort")
        
        # Height warnings
        if height_cm > 195:
            notes.append("Height is tall - consider long lengths")
        elif height_cm < 160:
            notes.append("Height is shorter - consider sleeve shortening")
        
        # Percentile analysis
        if percentiles['height_percentile'] < 10:
            notes.append("Height is below 10th percentile")
        elif percentiles['height_percentile'] > 90:
            notes.append("Height is above 90th percentile")
        
        return notes

class CustomerSimilarityEngine:
    """Customer similarity weighting based on 3,371 record concept"""
    
    def __init__(self):
        self.customer_database = self._load_synthetic_customer_data()
        self.similarity_threshold = 0.8
        
    def _load_synthetic_customer_data(self) -> pd.DataFrame:
        """Load synthetic customer data simulating 3,371 real records"""
        
        # Generate realistic customer data based on anthropometric research
        np.random.seed(42)  # For reproducible results
        
        n_customers = 3371
        
        # Generate height distribution (realistic male population)
        height_mean, height_std = 178, 7.5
        heights = np.random.normal(height_mean, height_std, n_customers)
        heights = np.clip(heights, 150, 210)  # Realistic range
        
        # Generate weight correlated with height
        weights = []
        for height in heights:
            # Weight correlated with height using anthropometric relationships
            base_weight = (height - 150) * 0.8 + 60
            weight_variation = np.random.normal(0, 12)
            weight = max(45, base_weight + weight_variation)
            weights.append(min(150, weight))
        
        # Generate fit preferences based on body type
        fit_preferences = []
        body_types = []
        
        for i, (height, weight) in enumerate(zip(heights, weights)):
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            height_weight_ratio = weight / (height_m)
            
            # Determine body type
            if bmi < 18.5:
                body_type = "Slim"
                fit_pref = np.random.choice(['slim', 'regular'], p=[0.7, 0.3])
            elif bmi > 30:
                body_type = "Broad"
                fit_pref = np.random.choice(['relaxed', 'regular'], p=[0.6, 0.4])
            elif height_weight_ratio > 1.1:
                body_type = "Athletic"
                fit_pref = np.random.choice(['slim', 'regular'], p=[0.5, 0.5])
            elif height_weight_ratio < 0.85:
                body_type = "Slender"
                fit_pref = np.random.choice(['slim', 'regular'], p=[0.6, 0.4])
            else:
                body_type = "Regular"
                fit_pref = np.random.choice(['slim', 'regular', 'relaxed'], p=[0.3, 0.5, 0.2])
            
            body_types.append(body_type)
            fit_preferences.append(fit_pref)
        
        # Generate size recommendations based on height/weight/fit
        sizes = []
        for height, weight, fit_pref in zip(heights, weights, fit_preferences):
            height_weight_ratio = weight / (height / 100)
            
            # Size calculation based on research
            if fit_pref == 'slim':
                if height_weight_ratio < 0.8:
                    size = '38'
                elif height_weight_ratio < 0.9:
                    size = '40'
                elif height_weight_ratio < 1.0:
                    size = '42'
                elif height_weight_ratio < 1.1:
                    size = '44'
                else:
                    size = '46'
                size += 'S'
            elif fit_pref == 'relaxed':
                if height_weight_ratio < 0.7:
                    size = '40'
                elif height_weight_ratio < 0.8:
                    size = '42'
                elif height_weight_ratio < 0.9:
                    size = '44'
                elif height_weight_ratio < 1.0:
                    size = '46'
                elif height_weight_ratio < 1.1:
                    size = '48'
                else:
                    size = '50'
                size += 'R'
            else:  # regular
                if height_weight_ratio < 0.75:
                    size = '38'
                elif height_weight_ratio < 0.85:
                    size = '40'
                elif height_weight_ratio < 0.95:
                    size = '42'
                elif height_weight_ratio < 1.05:
                    size = '44'
                elif height_weight_ratio < 1.15:
                    size = '46'
                elif height_weight_ratio < 1.25:
                    size = '48'
                else:
                    size = '50'
                size += 'R'
            
            # Add length suffix for tall users
            if height > 185:
                if height > 200:
                    size = size[:-1] + 'L'
                else:
                    # Regular length for 185-200cm
                    pass
            
            sizes.append(size)
        
        # Generate success rates (probability that customer was satisfied with size)
        success_rates = []
        for height, weight, size in zip(heights, weights, sizes):
            base_success = 0.85  # 85% base success rate
            
            # Adjust based on how "normal" the measurements are
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            
            if 22 <= bmi <= 25 and 170 <= height <= 185:
                base_success = 0.92  # Very typical measurements
            elif bmi < 18.5 or bmi > 30 or height < 160 or height > 200:
                base_success = 0.65  # Edge cases
            
            # Add some randomness
            success_rate = np.random.normal(base_success, 0.1)
            success_rate = np.clip(success_rate, 0.3, 0.99)
            success_rates.append(success_rate)
        
        # Create DataFrame
        customer_data = pd.DataFrame({
            'customer_id': range(1, n_customers + 1),
            'height_cm': heights,
            'weight_kg': weights,
            'fit_preference': fit_preferences,
            'body_type': body_types,
            'recommended_size': sizes,
            'success_rate': success_rates,
            'age_estimate': [AnthropometricValidator._estimate_age(h, w, w/((h/100)**2)) 
                           for h, w in zip(heights, weights)]
        })
        
        logger.info(f"Generated synthetic customer database with {len(customer_data)} records")
        return customer_data
    
    def find_similar_customers(self, height_cm: float, weight_kg: float, fit_pref: str, 
                             limit: int = 10) -> pd.DataFrame:
        """Find similar customers based on measurements and fit preference"""
        
        # Calculate similarity scores
        customer_data = self.customer_database.copy()
        
        # Multi-factor similarity calculation
        customer_data['height_diff'] = abs(customer_data['height_cm'] - height_cm)
        customer_data['weight_diff'] = abs(customer_data['weight_kg'] - weight_kg)
        customer_data['fit_match'] = (customer_data['fit_preference'] == fit_pref).astype(int)
        
        # Calculate composite similarity score (lower is better)
        # Normalize differences to 0-1 scale
        height_normalized = customer_data['height_diff'] / 50  # 50cm max difference
        weight_normalized = customer_data['weight_diff'] / 50  # 50kg max difference
        
        # Weighted similarity score
        similarity_score = (
            0.4 * height_normalized +
            0.4 * weight_normalized +
            0.2 * (1 - customer_data['fit_match'])  # Penalty for different fit
        )
        
        customer_data['similarity_score'] = similarity_score
        
        # Sort by similarity and return top matches
        similar_customers = customer_data.nsmallest(limit, 'similarity_score')
        
        return similar_customers[['customer_id', 'height_cm', 'weight_kg', 'fit_preference', 
                                'recommended_size', 'success_rate', 'similarity_score']]
    
    def get_similarity_weight(self, height_cm: float, weight_kg: float, fit_pref: str) -> float:
        """Calculate similarity weight for current measurements"""
        
        similar_customers = self.find_similar_customers(height_cm, weight_kg, fit_pref, limit=5)
        
        if len(similar_customers) == 0:
            return 1.0  # No similar customers, use base confidence
        
        # Calculate weighted average success rate
        total_weight = 0
        weighted_success = 0
        
        for _, customer in similar_customers.iterrows():
            # Inverse of similarity score (lower similarity = higher weight)
            weight = 1 / (1 + customer['similarity_score'])
            total_weight += weight
            weighted_success += weight * customer['success_rate']
        
        if total_weight > 0:
            avg_success_rate = weighted_success / total_weight
            # Convert to confidence multiplier (1.0 to 1.5 range)
            confidence_multiplier = 1.0 + (avg_success_rate - 0.85) * 2
            return np.clip(confidence_multiplier, 0.8, 1.5)
        else:
            return 1.0

class MLSizePredictor:
    """Machine Learning-based size prediction with SVR and GRNN models"""
    
    def __init__(self):
        self.svr_model = None
        self.grnn_model = None
        self.scaler = StandardScaler()
        self.size_encoder = {}
        self.reverse_size_encoder = {}
        self.is_trained = False
        
    def prepare_features(self, height_cm: float, weight_kg: float, fit_pref: str) -> np.ndarray:
        """Prepare features for ML prediction"""
        
        # Convert fit preference to numeric
        fit_mapping = {'slim': 0, 'regular': 1, 'relaxed': 2}
        fit_numeric = fit_mapping.get(fit_pref, 1)
        
        # Calculate anthropometric features
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        height_weight_ratio = weight_kg / (height_m)
        
        # Feature vector
        features = np.array([
            height_cm,
            weight_kg,
            bmi,
            height_weight_ratio,
            fit_numeric,
            height_m,
            weight_kg / height_m,  # Additional ratio
            height_cm * weight_kg  # Interaction term
        ])
        
        return features.reshape(1, -1)
    
    def train_models(self, customer_data: pd.DataFrame):
        """Train ML models on customer data"""
        
        logger.info("Training ML models...")
        
        # Prepare features and targets
        X = []
        y = []
        
        for _, row in customer_data.iterrows():
            features = self.prepare_features(row['height_cm'], row['weight_kg'], row['fit_preference'])
            X.append(features.flatten())
            y.append(row['recommended_size'])
        
        X = np.array(X)
        
        # Encode size labels
        unique_sizes = sorted(list(set(y)))
        self.size_encoder = {size: i for i, size in enumerate(unique_sizes)}
        self.reverse_size_encoder = {i: size for size, i in self.size_encoder.items()}
        
        y_encoded = [self.size_encoder[size] for size in y]
        y_encoded = np.array(y_encoded)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train SVR model
        logger.info("Training SVR model...")
        self.svr_model = SVR(kernel='rbf', C=100, gamma='scale', epsilon=0.1)
        self.svr_model.fit(X_scaled, y_encoded)
        
        # Train GRNN model (using MLPRegressor as approximation)
        logger.info("Training GRNN model...")
        self.grnn_model = MLPRegressor(
            hidden_layer_sizes=(50, 30),
            activation='relu',
            solver='adam',
            alpha=0.001,
            random_state=42
        )
        self.grnn_model.fit(X_scaled, y_encoded)
        
        # Evaluate models
        svr_pred = self.svr_model.predict(X_scaled)
        grnn_pred = self.grnn_model.predict(X_scaled)
        
        svr_accuracy = r2_score(y_encoded, svr_pred)
        grnn_accuracy = r2_score(y_encoded, grnn_pred)
        
        logger.info(f"SVR Model R² Score: {svr_accuracy:.3f}")
        logger.info(f"GRNN Model R² Score: {grnn_accuracy:.3f}")
        
        self.is_trained = True
        logger.info("ML models trained successfully")
    
    def predict_size(self, height_cm: float, weight_kg: float, fit_pref: str) -> Dict[str, Any]:
        """Predict size using ensemble of ML models"""
        
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
        
        # Prepare features
        features = self.prepare_features(height_cm, weight_kg, fit_pref)
        features_scaled = self.scaler.transform(features)
        
        # Get predictions from both models
        svr_pred_encoded = self.svr_model.predict(features_scaled)[0]
        grnn_pred_encoded = self.grnn_model.predict(features_scaled)[0]
        
        # Ensemble prediction (average)
        ensemble_pred_encoded = (svr_pred_encoded + grnn_pred_encoded) / 2
        
        # Round to nearest integer and convert to size
        size_idx = round(ensemble_pred_encoded)
        size_idx = np.clip(size_idx, 0, len(self.size_encoder) - 1)
        
        predicted_size = self.reverse_size_encoder[size_idx]
        
        # Calculate confidence based on model agreement
        svr_confidence = 1.0 / (1.0 + abs(svr_pred_encoded - ensemble_pred_encoded))
        grnn_confidence = 1.0 / (1.0 + abs(grnn_pred_encoded - ensemble_pred_encoded))
        
        model_confidence = (svr_confidence + grnn_confidence) / 2
        
        return {
            'predicted_size': predicted_size,
            'svr_prediction': self.reverse_size_encoder.get(round(svr_pred_encoded), predicted_size),
            'grnn_prediction': self.reverse_size_encoder.get(round(grnn_pred_encoded), predicted_size),
            'model_confidence': model_confidence,
            'ensemble_prediction': predicted_size
        }
    
    def save_models(self, filepath: str):
        """Save trained models"""
        model_data = {
            'svr_model': self.svr_model,
            'grnn_model': self.grnn_model,
            'scaler': self.scaler,
            'size_encoder': self.size_encoder,
            'reverse_size_encoder': self.reverse_size_encoder,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.svr_model = model_data['svr_model']
            self.grnn_model = model_data['grnn_model']
            self.scaler = model_data['scaler']
            self.size_encoder = model_data['size_encoder']
            self.reverse_size_encoder = model_data['reverse_size_encoder']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Models loaded from {filepath}")
        except FileNotFoundError:
            logger.warning(f"Model file {filepath} not found. Models will need to be trained.")

class EnhancedConfidenceScorer:
    """Enhanced confidence scoring using distance-based methods from academic research"""
    
    def __init__(self):
        self.confidence_weights = {
            'anthropometric': 0.3,
            'similarity': 0.25,
            'model_prediction': 0.25,
            'edge_case': 0.2
        }
    
    def calculate_confidence(self, height_cm: float, weight_kg: float, fit_pref: str,
                           predicted_size: str, ml_confidence: float, 
                           similarity_weight: float, anthropometric_data: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score"""
        
        # 1. Anthropometric confidence
        anthropometric_confidence = self._calculate_anthropometric_confidence(
            anthropometric_data, height_cm, weight_kg
        )
        
        # 2. Similarity confidence
        similarity_confidence = min(1.0, similarity_weight)
        
        # 3. Model prediction confidence
        model_confidence = ml_confidence
        
        # 4. Edge case handling
        edge_case_confidence = self._calculate_edge_case_confidence(
            height_cm, weight_kg, fit_pref, anthropometric_data
        )
        
        # Weighted ensemble
        overall_confidence = (
            self.confidence_weights['anthropometric'] * anthropometric_confidence +
            self.confidence_weights['similarity'] * similarity_confidence +
            self.confidence_weights['model_prediction'] * model_confidence +
            self.confidence_weights['edge_case'] * edge_case_confidence
        )
        
        return np.clip(overall_confidence, 0.0, 1.0)
    
    def _calculate_anthropometric_confidence(self, anthropometric_data: Dict[str, Any], 
                                           height_cm: float, weight_kg: float) -> float:
        """Calculate confidence based on anthropometric normalcy"""
        
        percentiles = anthropometric_data.get('percentiles', {})
        bmi = anthropometric_data.get('bmi', 25)
        
        # Height percentile confidence
        height_percentile = percentiles.get('height_percentile', 50)
        height_confidence = 1.0 - abs(height_percentile - 50) / 50
        
        # BMI confidence
        if 18.5 <= bmi <= 25:
            bmi_confidence = 1.0
        elif 16 <= bmi <= 30:
            bmi_confidence = 0.8
        else:
            bmi_confidence = 0.5
        
        # Combined anthropometric confidence
        return (height_confidence + bmi_confidence) / 2
    
    def _calculate_edge_case_confidence(self, height_cm: float, weight_kg: float, 
                                      fit_pref: str, anthropometric_data: Dict[str, Any]) -> float:
        """Calculate confidence based on edge case analysis"""
        
        bmi = anthropometric_data.get('bmi', 25)
        body_type = anthropometric_data.get('body_type', 'Regular')
        
        base_confidence = 0.8
        
        # Height edge cases
        if height_cm < 160 or height_cm > 200:
            base_confidence -= 0.2
        elif height_cm < 165 or height_cm > 195:
            base_confidence -= 0.1
        
        # BMI edge cases
        if bmi < 18.5 or bmi > 30:
            base_confidence -= 0.3
        elif bmi < 20 or bmi > 28:
            base_confidence -= 0.1
        
        # Body type edge cases
        if body_type in ['Slim', 'Broad']:
            base_confidence -= 0.1
        
        return max(0.1, base_confidence)
    
    def get_confidence_level(self, confidence: float) -> str:
        """Convert numerical confidence to human-readable level"""
        if confidence >= 0.85:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.65:
            return "Medium"
        elif confidence >= 0.55:
            return "Low"
        else:
            return "Very Low"

class EnhancedSuitSizeEngine:
    """Main enhanced sizing engine integrating all components"""
    
    def __init__(self):
        self.anthropometric_validator = AnthropometricValidator()
        self.similarity_engine = CustomerSimilarityEngine()
        self.ml_predictor = MLSizePredictor()
        self.confidence_scorer = EnhancedConfidenceScorer()
        
        # Initialize with synthetic customer data
        self.ml_predictor.train_models(self.similarity_engine.customer_database)
        
        logger.info("Enhanced SuitSize Engine initialized")
    
    def get_size_recommendation(self, height: float, weight: float, fit: str, unit: str = 'metric') -> Dict[str, Any]:
        """Get comprehensive size recommendation with all enhancements"""
        
        start_time = time.time()
        
        # 1. Anthropometric validation and analysis
        anthropometric_data = self.anthropometric_validator.validate_measurements(height, weight, unit)
        
        # 2. Customer similarity analysis
        height_cm = anthropometric_data['height_cm']
        weight_kg = anthropometric_data['weight_kg']
        
        similar_customers = self.similarity_engine.find_similar_customers(
            height_cm, weight_kg, fit, limit=5
        )
        similarity_weight = self.similarity_engine.get_similarity_weight(
            height_cm, weight_kg, fit
        )
        
        # 3. ML-based size prediction
        ml_prediction = self.ml_predictor.predict_size(height_cm, weight_kg, fit)
        
        # 4. Enhanced confidence scoring
        confidence = self.confidence_scorer.calculate_confidence(
            height_cm, weight_kg, fit, ml_prediction['predicted_size'],
            ml_prediction['model_confidence'], similarity_weight, anthropometric_data
        )
        
        confidence_level = self.confidence_scorer.get_confidence_level(confidence)
        
        # 5. Generate enhanced rationale
        rationale = self._generate_enhanced_rationale(
            height_cm, weight_kg, fit, ml_prediction['predicted_size'],
            anthropometric_data, similar_customers
        )
        
        # 6. Calculate recommended alterations
        alterations = self._calculate_enhanced_alterations(
            height_cm, weight_kg, fit, anthropometric_data
        )
        
        processing_time = time.time() - start_time
        
        # 7. Compile recommendation
        recommendation = {
            'size': ml_prediction['predicted_size'],
            'confidence': confidence,
            'confidenceLevel': confidence_level,
            'bodyType': anthropometric_data['body_type'],
            'rationale': rationale,
            'alterations': alterations,
            'measurements': {
                'height_cm': round(height_cm, 1),
                'weight_kg': round(weight_kg, 1),
                'bmi': round(anthropometric_data['bmi'], 1),
                'unit': unit
            },
            'similarCustomers': len(similar_customers),
            'similarityWeight': round(similarity_weight, 3),
            'mlModel': 'SVR+GRNN Ensemble',
            'modelConfidence': round(ml_prediction['model_confidence'], 3),
            'processingTime': round(processing_time * 1000, 1),  # ms
            'validationNotes': anthropometric_data['validation_notes'],
            'percentiles': anthropometric_data['percentiles']
        }
        
        return recommendation
    
    def _generate_enhanced_rationale(self, height_cm: float, weight_kg: float, fit: str,
                                   predicted_size: str, anthropometric_data: Dict[str, Any],
                                   similar_customers: pd.DataFrame) -> str:
        """Generate enhanced rationale with ML and similarity insights"""
        
        rationale_parts = [
            f"Based on your measurements ({height_cm:.0f}cm, {weight_kg:.0f}kg),",
            f"ML analysis suggests a {predicted_size} size with {fit} fit.",
            f"Your body type is classified as {anthropometric_data['body_type']}."
        ]
        
        # Add similarity insights
        if len(similar_customers) > 0:
            avg_success = similar_customers['success_rate'].mean()
            rationale_parts.append(
                f"Similar customers ({len(similar_customers)} matches) had {avg_success:.1%} success rate."
            )
        
        # Add percentile insights
        percentiles = anthropometric_data['percentiles']
        height_percentile = percentiles['height_percentile']
        
        if height_percentile < 10:
            rationale_parts.append("Your height is below the 10th percentile.")
        elif height_percentile > 90:
            rationale_parts.append("Your height is above the 90th percentile.")
        
        # Add BMI insights
        bmi = anthropometric_data['bmi']
        if bmi < 18.5:
            rationale_parts.append("BMI indicates underweight classification.")
        elif bmi > 30:
            rationale_parts.append("BMI indicates overweight classification.")
        
        return " ".join(rationale_parts)
    
    def _calculate_enhanced_alterations(self, height_cm: float, weight_kg: float, fit: str,
                                      anthropometric_data: Dict[str, Any]) -> List[str]:
        """Calculate enhanced alterations based on ML insights"""
        
        alterations = []
        body_type = anthropometric_data['body_type']
        bmi = anthropometric_data['bmi']
        
        # Body type specific alterations
        if body_type == "Athletic":
            alterations.extend([
                "Shoulder_width_adjustment",
                "Chest_let_out",
                "Armhole_modification"
            ])
        elif body_type == "Broad":
            alterations.extend([
                "Waist_let_out",
                "Trouser_widening",
                "Shoulder_width_adjustment"
            ])
        elif body_type == "Slim":
            alterations.extend([
                "Waist_take_in",
                "Sleeve_shortening",
                "Chest_take_in"
            ])
        elif body_type == "Slender":
            alterations.extend([
                "Waist_take_in",
                "Sleeve_shortening"
            ])
        else:  # Regular
            alterations.extend([
                "Minor_adjustments_as_needed"
            ])
        
        # Height-based alterations
        if height_cm > 200:
            alterations.append("Sleeve_lengthening")
            alterations.append("Trouser_lengthening")
        elif height_cm > 190:
            alterations.append("Sleeve_lengthening")
        elif height_cm < 160:
            alterations.append("Sleeve_shortening")
            alterations.append("Trouser_shortening")
        
        # Fit-specific alterations
        if fit == 'slim' and bmi > 25:
            alterations.append("Fit_relaxation_recommended")
        elif fit == 'relaxed' and bmi < 22:
            alterations.append("Fit_tightening_possible")
        
        return alterations
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics and performance metrics"""
        
        return {
            'customerDatabaseSize': len(self.similarity_engine.customer_database),
            'mlModelsTrained': self.ml_predictor.is_trained,
            'anthropometricFeatures': 8,
            'similarityFactors': ['height', 'weight', 'fit_preference'],
            'confidenceComponents': list(self.confidence_scorer.confidence_weights.keys()),
            'supportedSizes': list(self.ml_predictor.size_encoder.keys()),
            'supportedFits': ['slim', 'regular', 'relaxed'],
            'version': '2.0-ML-Enhanced'
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the enhanced engine
    engine = EnhancedSuitSizeEngine()
    
    # Test with various inputs
    test_cases = [
        {'height': 175, 'weight': 75, 'fit': 'regular', 'unit': 'metric'},
        {'height': 210, 'weight': 95, 'fit': 'regular', 'unit': 'metric'},
        {'height': 160, 'weight': 55, 'fit': 'slim', 'unit': 'metric'},
        {'height': 69, 'weight': 165, 'fit': 'regular', 'unit': 'imperial'}
    ]
    
    print("🧪 Testing Enhanced SuitSize Engine")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case}")
        recommendation = engine.get_size_recommendation(**test_case)
        
        print(f"✅ Recommended Size: {recommendation['size']}")
        print(f"📊 Confidence: {recommendation['confidence']:.1%} ({recommendation['confidenceLevel']})")
        print(f"👤 Body Type: {recommendation['bodyType']}")
        print(f"⚡ Processing Time: {recommendation['processingTime']}ms")
        print(f"🤝 Similar Customers: {recommendation['similarCustomers']}")
    
    # Engine statistics
    print(f"\n📈 Engine Statistics:")
    stats = engine.get_engine_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")