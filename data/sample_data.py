"""
Sample Data Generator
Generates sample carbon footprint data for training and testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(n_users=100, days_per_user=30):
    """
    Generate sample carbon footprint data for multiple users
    
    Args:
        n_users (int): Number of users to generate data for
        days_per_user (int): Number of days of data per user
        
    Returns:
        pandas.DataFrame: Sample data
    """
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for user_id in range(n_users):
        # Generate user profile (affects baseline activity levels)
        user_type = random.choice(['light', 'moderate', 'heavy'])
        
        # Set baseline activity levels based on user type
        if user_type == 'light':
            email_base = 10
            video_base = 1
            streaming_base = 2
            cloud_base = 2
            device_base = 6
        elif user_type == 'moderate':
            email_base = 25
            video_base = 2.5
            streaming_base = 4
            cloud_base = 5
            device_base = 8
        else:  # heavy
            email_base = 50
            video_base = 4
            streaming_base = 6
            cloud_base = 10
            device_base = 12
        
        # Generate daily data for this user
        start_date = datetime.now() - timedelta(days=days_per_user)
        
        for day in range(days_per_user):
            current_date = start_date + timedelta(days=day)
            
            # Add day-of-week and seasonal variations
            weekday = current_date.weekday()
            is_weekend = weekday >= 5
            
            # Weekend modifier (generally higher streaming, lower emails/calls)
            weekend_mod = 1.3 if is_weekend else 1.0
            work_mod = 0.7 if is_weekend else 1.0
            
            # Generate daily activities with some randomness
            emails = max(0, int(np.random.poisson(email_base * work_mod)))
            video_calls = max(0, np.random.gamma(2, video_base * work_mod / 2))
            streaming = max(0, np.random.gamma(2, streaming_base * weekend_mod / 2))
            cloud_storage = max(0, np.random.gamma(3, cloud_base / 3))
            device_usage = max(1, np.random.normal(device_base, 2))
            
            # Calculate CO2 emissions
            co2_emissions = (
                emails * 4.0 +  # 4g per email
                video_calls * 150.0 +  # 150g per hour
                streaming * 36.0 +  # 36g per hour
                cloud_storage * 10.0 +  # 10g per GB
                device_usage * 20.0  # 20g per hour
            )
            
            # Add some realistic noise
            noise = np.random.normal(0, co2_emissions * 0.1)
            co2_emissions = max(0, co2_emissions + noise)
            
            data.append({
                'user_id': user_id,
                'date': current_date.strftime('%Y-%m-%d'),
                'user_type': user_type,
                'weekday': weekday,
                'is_weekend': is_weekend,
                'emails': emails,
                'video_calls': round(video_calls, 2),
                'streaming': round(streaming, 2),
                'cloud_storage': round(cloud_storage, 2),
                'device_usage': round(device_usage, 2),
                'co2_emissions': round(co2_emissions, 2)
            })
    
    return pd.DataFrame(data)

def generate_user_journey_data(improvement_trend='gradual'):
    """
    Generate data showing a user's improvement journey over time
    
    Args:
        improvement_trend (str): Type of improvement ('gradual', 'dramatic', 'plateau')
        
    Returns:
        pandas.DataFrame: User journey data
    """
    np.random.seed(42)
    
    data = []
    days = 90  # 3 months of data
    start_date = datetime.now() - timedelta(days=days)
    
    # Starting values (high emissions)
    base_emissions = 3000  # Start with high emissions
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Calculate improvement factor based on trend type and day
        if improvement_trend == 'gradual':
            improvement_factor = 1 - (day / days) * 0.6  # 60% improvement over time
        elif improvement_trend == 'dramatic':
            if day < 30:
                improvement_factor = 1 - (day / 30) * 0.5  # 50% improvement in first month
            else:
                improvement_factor = 0.5  # Maintain improvement
        elif improvement_trend == 'plateau':
            if day < 45:
                improvement_factor = 1 - (day / 45) * 0.3  # 30% improvement then plateau
            else:
                improvement_factor = 0.7  # Plateau at 30% improvement
        else:
            improvement_factor = 1  # No improvement
        
        # Generate activities based on improvement
        target_emissions = base_emissions * improvement_factor
        
        # Reverse-engineer activities to hit target emissions
        # Distribute target emissions across activities proportionally
        emails = max(5, int(target_emissions * 0.15 / 4))  # 15% from emails
        video_calls = max(0.5, target_emissions * 0.25 / 150)  # 25% from video calls
        streaming = max(0.5, target_emissions * 0.30 / 36)  # 30% from streaming
        cloud_storage = max(1, target_emissions * 0.10 / 10)  # 10% from cloud
        device_usage = max(2, target_emissions * 0.20 / 20)  # 20% from device usage
        
        # Calculate actual emissions
        co2_emissions = (
            emails * 4.0 +
            video_calls * 150.0 +
            streaming * 36.0 +
            cloud_storage * 10.0 +
            device_usage * 20.0
        )
        
        # Add some randomness
        noise = np.random.normal(0, co2_emissions * 0.1)
        co2_emissions = max(0, co2_emissions + noise)
        
        data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_number': day + 1,
            'emails': int(emails),
            'video_calls': round(video_calls, 2),
            'streaming': round(streaming, 2),
            'cloud_storage': round(cloud_storage, 2),
            'device_usage': round(device_usage, 2),
            'co2_emissions': round(co2_emissions, 2),
            'improvement_factor': round(improvement_factor, 3),
            'target_emissions': round(target_emissions, 2)
        })
    
    return pd.DataFrame(data)

def get_global_averages():
    """
    Get global average carbon footprint data for comparison
    
    Returns:
        dict: Global averages for different activities
    """
    return {
        'daily_co2_average': 2500,  # grams per day
        'emails_average': 25,  # emails per day
        'video_calls_average': 2.0,  # hours per day
        'streaming_average': 3.5,  # hours per day
        'cloud_storage_average': 8.0,  # GB per day
        'device_usage_average': 8.5,  # hours per day
        'country_averages': {
            'USA': 3200,
            'Germany': 2100,
            'Japan': 1800,
            'India': 1200,
            'Brazil': 1600,
            'Global Average': 2500
        }
    }

def generate_eco_tips_data():
    """
    Generate data about eco tips effectiveness
    
    Returns:
        pandas.DataFrame: Eco tips effectiveness data
    """
    tips_data = [
        {
            'tip_category': 'Email Management',
            'tip_name': 'Batch Email Sending',
            'average_co2_reduction': 15,  # grams per day
            'difficulty': 'Easy',
            'adoption_rate': 0.85,
            'user_satisfaction': 4.2
        },
        {
            'tip_category': 'Video Calls',
            'tip_name': 'Audio-Only Meetings',
            'average_co2_reduction': 120,
            'difficulty': 'Easy',
            'adoption_rate': 0.65,
            'user_satisfaction': 3.8
        },
        {
            'tip_category': 'Streaming',
            'tip_name': 'Lower Video Quality',
            'average_co2_reduction': 18,
            'difficulty': 'Easy',
            'adoption_rate': 0.45,
            'user_satisfaction': 3.5
        },
        {
            'tip_category': 'Cloud Storage',
            'tip_name': 'Regular Cleanup',
            'average_co2_reduction': 50,
            'difficulty': 'Medium',
            'adoption_rate': 0.35,
            'user_satisfaction': 4.0
        },
        {
            'tip_category': 'Device Usage',
            'tip_name': 'Power Saving Mode',
            'average_co2_reduction': 40,
            'difficulty': 'Easy',
            'adoption_rate': 0.75,
            'user_satisfaction': 4.1
        },
        {
            'tip_category': 'General',
            'tip_name': 'Dark Mode',
            'average_co2_reduction': 25,
            'difficulty': 'Easy',
            'adoption_rate': 0.90,
            'user_satisfaction': 4.4
        }
    ]
    
    return pd.DataFrame(tips_data)

# Example usage for testing
if __name__ == "__main__":
    # Generate sample data
    sample_df = generate_sample_data(n_users=10, days_per_user=7)
    print("Sample Data Shape:", sample_df.shape)
    print("\nSample Data Head:")
    print(sample_df.head())
    
    # Generate journey data
    journey_df = generate_user_journey_data('gradual')
    print("\nJourney Data Shape:", journey_df.shape)
    print("\nJourney Data Head:")
    print(journey_df.head())
    
    # Get global averages
    global_avg = get_global_averages()
    print("\nGlobal Averages:")
    print(global_avg)
    
    # Generate eco tips data
    tips_df = generate_eco_tips_data()
    print("\nEco Tips Data:")
    print(tips_df)
