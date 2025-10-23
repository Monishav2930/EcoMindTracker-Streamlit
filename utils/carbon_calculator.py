"""
Carbon Calculator Module
Calculates CO2 emissions for various digital activities
"""

class CarbonCalculator:
    def __init__(self):
        # CO2 emission factors (in grams)
        self.emission_factors = {
            'email': 4.0,  # grams per email
            'video_call': 150.0,  # grams per hour
            'streaming': 36.0,  # grams per hour
            'cloud_storage': 10.0,  # grams per GB per day
            'device_usage': 20.0,  # grams per hour (average for laptop/desktop)
        }
    
    def calculate_daily_footprint(self, emails, video_calls_hours, streaming_hours, cloud_storage_gb, device_hours):
        """
        Calculate total daily CO2 footprint from digital activities
        
        Args:
            emails (int): Number of emails sent
            video_calls_hours (float): Hours spent on video calls
            streaming_hours (float): Hours spent streaming
            cloud_storage_gb (float): Cloud storage used in GB
            device_hours (float): Total device usage in hours
            
        Returns:
            float: Total CO2 emissions in grams
        """
        email_co2 = emails * self.emission_factors['email']
        video_co2 = video_calls_hours * self.emission_factors['video_call']
        streaming_co2 = streaming_hours * self.emission_factors['streaming']
        storage_co2 = cloud_storage_gb * self.emission_factors['cloud_storage']
        device_co2 = device_hours * self.emission_factors['device_usage']
        
        total_co2 = email_co2 + video_co2 + streaming_co2 + storage_co2 + device_co2
        
        return round(total_co2, 2)
    
    def get_activity_breakdown(self, emails, video_calls_hours, streaming_hours, cloud_storage_gb, device_hours):
        """
        Get breakdown of CO2 emissions by activity
        
        Returns:
            dict: Dictionary with activity names as keys and CO2 values as values
        """
        return {
            'Emails': emails * self.emission_factors['email'],
            'Video Calls': video_calls_hours * self.emission_factors['video_call'],
            'Streaming': streaming_hours * self.emission_factors['streaming'],
            'Cloud Storage': cloud_storage_gb * self.emission_factors['cloud_storage'],
            'Device Usage': device_hours * self.emission_factors['device_usage']
        }
    
    def calculate_weekly_footprint(self, daily_logs):
        """
        Calculate total weekly footprint from daily logs
        
        Args:
            daily_logs (list): List of daily log dictionaries
            
        Returns:
            float: Total weekly CO2 emissions in grams
        """
        if not daily_logs:
            return 0.0
        
        total_weekly = sum(log['co2_grams'] for log in daily_logs[-7:])  # Last 7 days
        return round(total_weekly, 2)
    
    def calculate_monthly_footprint(self, daily_logs):
        """
        Calculate total monthly footprint from daily logs
        
        Args:
            daily_logs (list): List of daily log dictionaries
            
        Returns:
            float: Total monthly CO2 emissions in grams
        """
        if not daily_logs:
            return 0.0
        
        total_monthly = sum(log['co2_grams'] for log in daily_logs[-30:])  # Last 30 days
        return round(total_monthly, 2)
    
    def get_efficiency_score(self, daily_co2):
        """
        Calculate efficiency score based on daily CO2 emissions
        
        Args:
            daily_co2 (float): Daily CO2 emissions in grams
            
        Returns:
            int: Efficiency score (0-100)
        """
        # Base score of 100, subtract points based on emissions
        # Average global digital footprint is ~2500g per day
        global_avg = 2500
        
        if daily_co2 <= global_avg * 0.5:  # 50% below average
            return 100
        elif daily_co2 <= global_avg:  # At or below average
            return max(80, 100 - int((daily_co2 - global_avg * 0.5) / (global_avg * 0.5) * 20))
        else:  # Above average
            return max(0, 80 - int((daily_co2 - global_avg) / global_avg * 80))
