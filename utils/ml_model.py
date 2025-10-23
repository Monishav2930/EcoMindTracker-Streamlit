"""
Machine Learning Carbon Predictor
Uses scikit-learn to predict future carbon emissions based on user behavior
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class CarbonPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Try to load existing model, otherwise train new one
        self.load_or_train_model()
    
    def load_or_train_model(self):
        """
        Load existing model or train a new one with synthetic data
        """
        try:
            # Try to load existing model (in a real deployment, this would be a saved model)
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Generate training data
            training_data = self.generate_training_data()
            self.train_model(training_data)
            
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to simple calculation
            self.model = None
    
    def generate_training_data(self, n_samples=1000):
        """
        Generate synthetic training data for the carbon prediction model
        
        Args:
            n_samples (int): Number of samples to generate
            
        Returns:
            pandas.DataFrame: Training data
        """
        np.random.seed(42)
        
        # Generate realistic activity data
        emails = np.random.poisson(25, n_samples)  # Average 25 emails per day
        video_calls = np.random.gamma(2, 1.5, n_samples)  # Average 3 hours, right-skewed
        streaming = np.random.gamma(2, 2, n_samples)  # Average 4 hours, right-skewed
        cloud_storage = np.random.gamma(3, 2, n_samples)  # Average 6GB, right-skewed
        device_usage = np.random.normal(8, 2, n_samples)  # Average 8 hours, normal distribution
        
        # Ensure non-negative values
        video_calls = np.maximum(0, video_calls)
        streaming = np.maximum(0, streaming)
        cloud_storage = np.maximum(0, cloud_storage)
        device_usage = np.maximum(1, device_usage)  # At least 1 hour device usage
        
        # Calculate CO2 emissions using carbon calculator logic
        co2_emissions = (
            emails * 4.0 +  # 4g per email
            video_calls * 150.0 +  # 150g per hour
            streaming * 36.0 +  # 36g per hour
            cloud_storage * 10.0 +  # 10g per GB
            device_usage * 20.0  # 20g per hour
        )
        
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 20, n_samples)
        co2_emissions = np.maximum(0, co2_emissions + noise)
        
        # Create DataFrame
        data = pd.DataFrame({
            'emails': emails,
            'video_calls': video_calls,
            'streaming': streaming,
            'cloud_storage': cloud_storage,
            'device_usage': device_usage,
            'co2_emissions': co2_emissions
        })
        
        return data
    
    def train_model(self, training_data):
        """
        Train the carbon prediction model
        
        Args:
            training_data (pandas.DataFrame): Training data
        """
        # Prepare features and target
        features = ['emails', 'video_calls', 'streaming', 'cloud_storage', 'device_usage']
        X = training_data[features]
        y = training_data['co2_emissions']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate accuracy
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        self.is_trained = True
    
    def predict_emissions(self, emails, video_calls, streaming, cloud_storage, device_usage, days=1):
        """
        Predict carbon emissions for given activities
        
        Args:
            emails (int): Number of emails per day
            video_calls (float): Hours of video calls per day
            streaming (float): Hours of streaming per day
            cloud_storage (float): GB of cloud storage per day
            device_usage (float): Hours of device usage per day
            days (int): Number of days to predict for
            
        Returns:
            float: Predicted CO2 emissions in grams
        """
        if not self.is_trained or self.model is None:
            # Fallback to simple calculation
            daily_co2 = (
                emails * 4.0 +
                video_calls * 150.0 +
                streaming * 36.0 +
                cloud_storage * 10.0 +
                device_usage * 20.0
            )
            return daily_co2 * days
        
        # Prepare input data
        input_data = np.array([[emails, video_calls, streaming, cloud_storage, device_usage]])
        input_scaled = self.scaler.transform(input_data)
        
        # Make prediction
        daily_prediction = self.model.predict(input_scaled)[0]
        
        # Multiply by number of days
        total_prediction = daily_prediction * days
        
        return max(0, total_prediction)  # Ensure non-negative
    
    def predict_with_confidence(self, emails, video_calls, streaming, cloud_storage, device_usage, days=1):
        """
        Predict carbon emissions with confidence interval
        
        Args:
            emails (int): Number of emails per day
            video_calls (float): Hours of video calls per day
            streaming (float): Hours of streaming per day
            cloud_storage (float): GB of cloud storage per day
            device_usage (float): Hours of device usage per day
            days (int): Number of days to predict for
            
        Returns:
            tuple: (prediction, lower_bound, upper_bound)
        """
        if not self.is_trained or self.model is None:
            prediction = self.predict_emissions(emails, video_calls, streaming, cloud_storage, device_usage, days)
            return prediction, prediction * 0.8, prediction * 1.2
        
        # For Random Forest, we can get confidence intervals using individual tree predictions
        input_data = np.array([[emails, video_calls, streaming, cloud_storage, device_usage]])
        input_scaled = self.scaler.transform(input_data)
        
        # Get predictions from all trees
        tree_predictions = []
        for tree in self.model.estimators_:
            pred = tree.predict(input_scaled)[0]
            tree_predictions.append(pred)
        
        tree_predictions = np.array(tree_predictions) * days
        
        mean_pred = np.mean(tree_predictions)
        std_pred = np.std(tree_predictions)
        
        # 95% confidence interval (approximately)
        lower_bound = mean_pred - 1.96 * std_pred
        upper_bound = mean_pred + 1.96 * std_pred
        
        return max(0, mean_pred), max(0, lower_bound), upper_bound
    
    def get_feature_importance(self):
        """
        Get feature importance from the trained model
        
        Returns:
            dict: Dictionary with feature names and their importance scores
        """
        if not self.is_trained or self.model is None:
            return {}
        
        features = ['emails', 'video_calls', 'streaming', 'cloud_storage', 'device_usage']
        importance_scores = self.model.feature_importances_
        
        return dict(zip(features, importance_scores))
    
    def predict_optimization_impact(self, current_activities, optimized_activities, days=1):
        """
        Predict the impact of optimization on carbon emissions
        
        Args:
            current_activities (dict): Current activity levels
            optimized_activities (dict): Optimized activity levels
            days (int): Number of days to predict for
            
        Returns:
            dict: Prediction results with current, optimized, and savings
        """
        current_co2 = self.predict_emissions(
            current_activities.get('emails', 0),
            current_activities.get('video_calls', 0),
            current_activities.get('streaming', 0),
            current_activities.get('cloud_storage', 0),
            current_activities.get('device_usage', 0),
            days
        )
        
        optimized_co2 = self.predict_emissions(
            optimized_activities.get('emails', 0),
            optimized_activities.get('video_calls', 0),
            optimized_activities.get('streaming', 0),
            optimized_activities.get('cloud_storage', 0),
            optimized_activities.get('device_usage', 0),
            days
        )
        
        savings = current_co2 - optimized_co2
        savings_percent = (savings / current_co2 * 100) if current_co2 > 0 else 0
        
        return {
            'current_co2': current_co2,
            'optimized_co2': optimized_co2,
            'savings_co2': savings,
            'savings_percent': savings_percent
        }
