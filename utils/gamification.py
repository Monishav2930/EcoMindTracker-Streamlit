"""
Gamification System
Handles user levels, badges, and scoring for EcoMind
"""

import math
from datetime import datetime, timedelta

class GamificationSystem:
    def __init__(self):
        self.levels = {
            'Bronze': {'min_score': 0, 'max_score': 100, 'color': '#CD7F32'},
            'Silver': {'min_score': 101, 'max_score': 250, 'color': '#C0C0C0'},
            'Gold': {'min_score': 251, 'max_score': 500, 'color': '#FFD700'},
            'Platinum': {'min_score': 501, 'max_score': 1000, 'color': '#E5E4E2'},
            'Diamond': {'min_score': 1001, 'max_score': float('inf'), 'color': '#B9F2FF'}
        }
        
        self.badges = {
            'First Steps': {
                'description': 'Track your first day of carbon emissions',
                'icon': '👶',
                'requirement': 'track_first_day'
            },
            'Week Warrior': {
                'description': 'Track emissions for 7 consecutive days',
                'icon': '📅',
                'requirement': 'track_7_days'
            },
            'Eco Novice': {
                'description': 'Reduce daily emissions below 2000g',
                'icon': '🌱',
                'requirement': 'below_2000g'
            },
            'Green Guardian': {
                'description': 'Reduce daily emissions below 1500g',
                'icon': '🌿',
                'requirement': 'below_1500g'
            },
            'Carbon Crusher': {
                'description': 'Reduce daily emissions below 1000g',
                'icon': '💚',
                'requirement': 'below_1000g'
            },
            'Eco Champion': {
                'description': 'Reduce daily emissions below 500g',
                'icon': '🏆',
                'requirement': 'below_500g'
            },
            'Consistency King': {
                'description': 'Track emissions for 30 consecutive days',
                'icon': '👑',
                'requirement': 'track_30_days'
            },
            'Improvement Master': {
                'description': 'Reduce emissions by 50% from your starting average',
                'icon': '📈',
                'requirement': 'reduce_50_percent'
            }
        }
        
        self.user_score = 0
        self.earned_badges = []
        self.current_level = 'Bronze'
    
    def calculate_daily_score(self, daily_co2):
        """
        Calculate score for a single day based on CO2 emissions
        
        Args:
            daily_co2 (float): Daily CO2 emissions in grams
            
        Returns:
            int: Points earned for the day
        """
        global_avg = 2500  # Average global daily digital carbon footprint
        
        # Base scoring system - more points for lower emissions
        if daily_co2 <= 500:  # Excellent
            return 20
        elif daily_co2 <= 1000:  # Very good
            return 15
        elif daily_co2 <= 1500:  # Good
            return 10
        elif daily_co2 <= 2000:  # Fair
            return 5
        elif daily_co2 <= global_avg:  # Below average
            return 2
        else:  # Above average
            return 1
    
    def update_score(self, daily_co2):
        """
        Update user's total score
        
        Args:
            daily_co2 (float): Daily CO2 emissions in grams
        """
        daily_points = self.calculate_daily_score(daily_co2)
        self.user_score += daily_points
        self.current_level = self.get_current_level()
        return daily_points
    
    def get_current_level(self):
        """
        Get current level based on total score
        
        Returns:
            str: Current level name
        """
        for level_name, level_info in self.levels.items():
            if level_info['min_score'] <= self.user_score <= level_info['max_score']:
                return level_name
        return 'Diamond'  # Highest level
    
    def get_level_progress(self):
        """
        Get progress towards next level as percentage
        
        Returns:
            float: Progress percentage (0-100)
        """
        current_level_info = self.levels[self.current_level]
        
        if current_level_info['max_score'] == float('inf'):
            return 100.0  # Max level reached
        
        level_range = current_level_info['max_score'] - current_level_info['min_score']
        current_progress = self.user_score - current_level_info['min_score']
        
        progress_percent = (current_progress / level_range) * 100
        return min(100.0, max(0.0, progress_percent))
    
    def get_next_level_info(self):
        """
        Get information about the next level
        
        Returns:
            dict: Next level information or None if at max level
        """
        level_names = list(self.levels.keys())
        current_index = level_names.index(self.current_level)
        
        if current_index < len(level_names) - 1:
            next_level_name = level_names[current_index + 1]
            next_level_info = self.levels[next_level_name]
            points_needed = next_level_info['min_score'] - self.user_score
            
            return {
                'name': next_level_name,
                'points_needed': max(0, points_needed),
                'color': next_level_info['color']
            }
        
        return None  # Already at max level
    
    def check_badges(self, user_logs):
        """
        Check and award badges based on user activity
        
        Args:
            user_logs (list): List of user's daily activity logs
            
        Returns:
            list: List of newly earned badge names
        """
        newly_earned = []
        
        if not user_logs:
            return newly_earned
        
        # Convert logs to DataFrame for easier analysis
        import pandas as pd
        df = pd.DataFrame(user_logs)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Check First Steps badge
        if 'First Steps' not in self.earned_badges and len(user_logs) >= 1:
            self.earned_badges.append('First Steps')
            newly_earned.append('First Steps')
        
        # Check Week Warrior badge (7 consecutive days)
        if 'Week Warrior' not in self.earned_badges and len(user_logs) >= 7:
            # Check if there are 7 consecutive days
            consecutive_days = self._check_consecutive_days(df, 7)
            if consecutive_days:
                self.earned_badges.append('Week Warrior')
                newly_earned.append('Week Warrior')
        
        # Check Consistency King badge (30 consecutive days)
        if 'Consistency King' not in self.earned_badges and len(user_logs) >= 30:
            consecutive_days = self._check_consecutive_days(df, 30)
            if consecutive_days:
                self.earned_badges.append('Consistency King')
                newly_earned.append('Consistency King')
        
        # Check emission-based badges
        recent_emissions = df['co2_grams'].tail(7).mean()  # Average of last 7 days
        
        emission_badges = [
            ('Eco Novice', 2000),
            ('Green Guardian', 1500),
            ('Carbon Crusher', 1000),
            ('Eco Champion', 500)
        ]
        
        for badge_name, threshold in emission_badges:
            if badge_name not in self.earned_badges and recent_emissions < threshold:
                self.earned_badges.append(badge_name)
                newly_earned.append(badge_name)
        
        # Check Improvement Master badge (50% reduction)
        if 'Improvement Master' not in self.earned_badges and len(user_logs) >= 14:
            first_week_avg = df['co2_grams'].head(7).mean()
            last_week_avg = df['co2_grams'].tail(7).mean()
            
            if first_week_avg > 0 and (first_week_avg - last_week_avg) / first_week_avg >= 0.5:
                self.earned_badges.append('Improvement Master')
                newly_earned.append('Improvement Master')
        
        return newly_earned
    
    def _check_consecutive_days(self, df, required_days):
        """
        Check if there are enough consecutive tracking days
        
        Args:
            df (pandas.DataFrame): DataFrame with date column
            required_days (int): Number of consecutive days required
            
        Returns:
            bool: True if consecutive days requirement is met
        """
        if len(df) < required_days:
            return False
        
        # Check if the last N days are consecutive
        last_n_days = df.tail(required_days)
        dates = last_n_days['date'].dt.date
        
        # Check if dates are consecutive
        for i in range(1, len(dates)):
            if (dates.iloc[i] - dates.iloc[i-1]).days != 1:
                return False
        
        return True
    
    def get_badges(self):
        """
        Get list of earned badges
        
        Returns:
            list: List of earned badge names
        """
        return self.earned_badges.copy()
    
    def get_badge_info(self, badge_name):
        """
        Get information about a specific badge
        
        Args:
            badge_name (str): Name of the badge
            
        Returns:
            dict: Badge information
        """
        return self.badges.get(badge_name, {})
    
    def get_achievement_summary(self, user_logs):
        """
        Get a summary of user's achievements
        
        Args:
            user_logs (list): List of user's daily activity logs
            
        Returns:
            dict: Achievement summary
        """
        total_days = len(user_logs)
        total_co2 = sum(log['co2_grams'] for log in user_logs) if user_logs else 0
        avg_daily_co2 = total_co2 / total_days if total_days > 0 else 0
        
        # Calculate improvement over time
        improvement = 0
        if total_days >= 7:
            import pandas as pd
            df = pd.DataFrame(user_logs)
            first_week_avg = df['co2_grams'].head(7).mean()
            last_week_avg = df['co2_grams'].tail(7).mean()
            
            if first_week_avg > 0:
                improvement = (first_week_avg - last_week_avg) / first_week_avg * 100
        
        return {
            'current_level': self.current_level,
            'total_score': self.user_score,
            'level_progress': self.get_level_progress(),
            'badges_earned': len(self.earned_badges),
            'total_badges': len(self.badges),
            'total_days_tracked': total_days,
            'average_daily_co2': avg_daily_co2,
            'improvement_percent': improvement,
            'next_level': self.get_next_level_info()
        }
