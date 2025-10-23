"""
Eco Recommendation Engine
Provides personalized recommendations based on user's digital carbon footprint
"""

import random
from datetime import datetime

class EcoRecommender:
    def __init__(self):
        self.recommendations = {
            'email': [
                {
                    'title': 'Batch Your Emails',
                    'description': 'Instead of sending emails throughout the day, compose and send them in batches. This reduces server load and energy consumption.',
                    'co2_savings': 15,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Unsubscribe from Unused Lists',
                    'description': 'Clean up your inbox by unsubscribing from newsletters and promotions you don\'t read. Less emails = less server energy.',
                    'co2_savings': 20,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Use Text Instead of Images',
                    'description': 'When possible, use text-based content instead of images or attachments in your emails to reduce data transfer.',
                    'co2_savings': 10,
                    'difficulty': 'easy'
                }
            ],
            'video_calls': [
                {
                    'title': 'Turn Off Video When Not Needed',
                    'description': 'Audio-only calls use up to 96% less bandwidth than video calls. Use video only when necessary.',
                    'co2_savings': 140,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Optimize Your Background',
                    'description': 'Use a simple, static background or turn off virtual backgrounds to reduce processing power.',
                    'co2_savings': 30,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Close Unnecessary Apps',
                    'description': 'Close other applications during video calls to reduce CPU usage and energy consumption.',
                    'co2_savings': 25,
                    'difficulty': 'easy'
                }
            ],
            'streaming': [
                {
                    'title': 'Lower Video Quality',
                    'description': 'Watching in standard definition instead of HD can reduce your carbon footprint by up to 50%.',
                    'co2_savings': 18,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Download for Offline Viewing',
                    'description': 'Download content when on Wi-Fi for offline viewing instead of streaming multiple times.',
                    'co2_savings': 25,
                    'difficulty': 'medium'
                },
                {
                    'title': 'Use Audio-Only for Background Content',
                    'description': 'For podcasts or music, turn off the video portion to save bandwidth and energy.',
                    'co2_savings': 30,
                    'difficulty': 'easy'
                }
            ],
            'cloud_storage': [
                {
                    'title': 'Regular Cloud Cleanup',
                    'description': 'Delete old files, duplicates, and unused data from your cloud storage to reduce server energy consumption.',
                    'co2_savings': 50,
                    'difficulty': 'medium'
                },
                {
                    'title': 'Use File Compression',
                    'description': 'Compress large files before uploading to reduce storage space and transfer energy.',
                    'co2_savings': 15,
                    'difficulty': 'medium'
                },
                {
                    'title': 'Choose Eco-Friendly Providers',
                    'description': 'Use cloud providers that run on renewable energy sources when possible.',
                    'co2_savings': 100,
                    'difficulty': 'hard'
                }
            ],
            'device_usage': [
                {
                    'title': 'Enable Power Saving Mode',
                    'description': 'Activate your device\'s power saving mode to reduce energy consumption automatically.',
                    'co2_savings': 40,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Close Idle Browser Tabs',
                    'description': 'Each open tab consumes memory and CPU. Close tabs you\'re not actively using.',
                    'co2_savings': 12,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Adjust Screen Brightness',
                    'description': 'Lower your screen brightness to reduce power consumption, especially on battery-powered devices.',
                    'co2_savings': 8,
                    'difficulty': 'easy'
                }
            ],
            'general': [
                {
                    'title': 'Use Dark Mode',
                    'description': 'Dark mode uses less energy on OLED screens and is easier on your eyes too.',
                    'co2_savings': 20,
                    'difficulty': 'easy'
                },
                {
                    'title': 'Schedule Regular Digital Detox',
                    'description': 'Take breaks from digital devices. Even 1 hour offline per day makes a difference.',
                    'co2_savings': 35,
                    'difficulty': 'medium'
                },
                {
                    'title': 'Use Ad Blockers',
                    'description': 'Ad blockers reduce data consumption by blocking energy-intensive advertisements.',
                    'co2_savings': 28,
                    'difficulty': 'easy'
                }
            ]
        }
    
    def get_recommendations(self, user_log):
        """
        Get personalized recommendations based on user's activity log
        
        Args:
            user_log (dict): Dictionary containing user's daily activities
            
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        # Analyze user's highest impact activities
        activities = {
            'emails': user_log.get('emails', 0) * 4,
            'video_calls': user_log.get('video_calls', 0) * 150,
            'streaming': user_log.get('streaming', 0) * 36,
            'cloud_storage': user_log.get('cloud_storage', 0) * 10,
            'device_usage': user_log.get('device_usage', 0) * 20
        }
        
        # Sort activities by CO2 impact (highest first)
        sorted_activities = sorted(activities.items(), key=lambda x: x[1], reverse=True)
        
        # Get recommendations for top 3 activities
        for activity, co2_amount in sorted_activities[:3]:
            if co2_amount > 0:  # Only recommend if user actually does this activity
                activity_key = activity
                if activity == 'video_calls':
                    activity_key = 'video_calls'
                elif activity == 'cloud_storage':
                    activity_key = 'cloud_storage'
                elif activity == 'device_usage':
                    activity_key = 'device_usage'
                
                if activity_key in self.recommendations:
                    # Get a random recommendation for this activity
                    activity_recs = self.recommendations[activity_key]
                    if activity_recs:
                        recommendations.append(random.choice(activity_recs))
        
        # Fill remaining slots with general recommendations
        while len(recommendations) < 3:
            general_recs = self.recommendations['general']
            rec = random.choice(general_recs)
            if rec not in recommendations:  # Avoid duplicates
                recommendations.append(rec)
        
        return recommendations
    
    def get_general_recommendations(self):
        """
        Get general eco recommendations for new users
        
        Returns:
            list: List of general recommendation dictionaries
        """
        all_easy_recs = []
        
        for category in self.recommendations:
            for rec in self.recommendations[category]:
                if rec['difficulty'] == 'easy':
                    all_easy_recs.append(rec)
        
        # Return 3 random easy recommendations
        return random.sample(all_easy_recs, min(3, len(all_easy_recs)))
    
    def get_recommendations_by_category(self, category):
        """
        Get all recommendations for a specific category
        
        Args:
            category (str): Category name (email, video_calls, streaming, etc.)
            
        Returns:
            list: List of recommendations for the category
        """
        return self.recommendations.get(category, [])
    
    def get_advanced_recommendations(self, user_logs):
        """
        Get advanced recommendations based on user's historical data
        
        Args:
            user_logs (list): List of daily activity logs
            
        Returns:
            list: List of advanced recommendation dictionaries
        """
        if not user_logs:
            return self.get_general_recommendations()
        
        # Analyze patterns over time
        total_days = len(user_logs)
        
        avg_activities = {
            'emails': sum(log.get('emails', 0) for log in user_logs) / total_days,
            'video_calls': sum(log.get('video_calls', 0) for log in user_logs) / total_days,
            'streaming': sum(log.get('streaming', 0) for log in user_logs) / total_days,
            'cloud_storage': sum(log.get('cloud_storage', 0) for log in user_logs) / total_days,
            'device_usage': sum(log.get('device_usage', 0) for log in user_logs) / total_days
        }
        
        recommendations = []
        
        # High usage patterns get harder difficulty recommendations
        for activity, avg_usage in avg_activities.items():
            activity_key = activity
            if activity == 'video_calls':
                activity_key = 'video_calls'
            elif activity == 'cloud_storage':
                activity_key = 'cloud_storage'
            elif activity == 'device_usage':
                activity_key = 'device_usage'
            
            if activity_key in self.recommendations:
                # Choose difficulty based on usage level
                if avg_usage > 50:  # High usage
                    hard_recs = [r for r in self.recommendations[activity_key] if r['difficulty'] == 'hard']
                    if hard_recs:
                        recommendations.extend(random.sample(hard_recs, min(1, len(hard_recs))))
                elif avg_usage > 20:  # Medium usage
                    med_recs = [r for r in self.recommendations[activity_key] if r['difficulty'] == 'medium']
                    if med_recs:
                        recommendations.extend(random.sample(med_recs, min(1, len(med_recs))))
        
        # Fill with general recommendations if needed
        while len(recommendations) < 3:
            general_recs = self.recommendations['general']
            rec = random.choice(general_recs)
            if rec not in recommendations:
                recommendations.append(rec)
        
        return recommendations[:3]
