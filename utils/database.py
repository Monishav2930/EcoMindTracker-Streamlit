"""
Database utility module for EcoMind
Handles all PostgreSQL database operations
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.environ.get('DATABASE_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable not set. Please configure your database connection.")
        
        # Test connection on initialization
        try:
            conn = psycopg2.connect(self.connection_string)
            conn.close()
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
        
        # Ensure schema exists
        self._ensure_schema()
        
    def _ensure_schema(self):
        """Ensure required database schema exists"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255),
            joined_date DATE NOT NULL DEFAULT CURRENT_DATE,
            current_level VARCHAR(50) DEFAULT 'Bronze',
            total_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            log_date DATE NOT NULL,
            emails INTEGER DEFAULT 0,
            video_calls DECIMAL(5,2) DEFAULT 0,
            streaming DECIMAL(5,2) DEFAULT 0,
            cloud_storage DECIMAL(5,2) DEFAULT 0,
            device_usage DECIMAL(5,2) DEFAULT 0,
            co2_grams DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, log_date)
        );

        CREATE TABLE IF NOT EXISTS user_badges (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            badge_name VARCHAR(100) NOT NULL,
            earned_date DATE NOT NULL DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, badge_name)
        );

        CREATE INDEX IF NOT EXISTS idx_activity_logs_user_date ON activity_logs(user_id, log_date DESC);
        CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id);
        """
        
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                conn.commit()
            conn.close()
        except Exception as e:
            raise ConnectionError(f"Failed to initialize database schema: {e}")
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.connection_string)
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Database connection failed: {e}")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                if fetch:
                    results = cur.fetchall()
                    conn.commit()
                    return results
                else:
                    conn.commit()
                    return None
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = None):
        """Execute an insert query and return the inserted ID"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                conn.commit()
                return result
        finally:
            conn.close()
    
    # User operations
    def create_user(self, username: str, email: str = None) -> int:
        """Create a new user and return user ID"""
        query = """
            INSERT INTO users (username, email, joined_date, current_level, total_score)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
        """
        result = self.execute_insert(
            query, 
            (username, email, date.today(), 'Bronze', 0)
        )
        return result['id'] if result else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        results = self.execute_query(query, (username,))
        return dict(results[0]) if results else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        results = self.execute_query(query, (user_id,))
        return dict(results[0]) if results else None
    
    def update_user_score(self, user_id: int, total_score: int, current_level: str):
        """Update user's total score and level"""
        query = """
            UPDATE users 
            SET total_score = %s, current_level = %s
            WHERE id = %s
        """
        self.execute_query(query, (total_score, current_level, user_id), fetch=False)
    
    # Activity log operations
    def add_activity_log(self, user_id: int, log_date: date, emails: int, 
                        video_calls: float, streaming: float, cloud_storage: float,
                        device_usage: float, co2_grams: float):
        """Add or update activity log for a specific date"""
        query = """
            INSERT INTO activity_logs 
            (user_id, log_date, emails, video_calls, streaming, cloud_storage, device_usage, co2_grams)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, log_date) 
            DO UPDATE SET 
                emails = EXCLUDED.emails,
                video_calls = EXCLUDED.video_calls,
                streaming = EXCLUDED.streaming,
                cloud_storage = EXCLUDED.cloud_storage,
                device_usage = EXCLUDED.device_usage,
                co2_grams = EXCLUDED.co2_grams
            RETURNING id
        """
        return self.execute_insert(
            query,
            (user_id, log_date, emails, video_calls, streaming, cloud_storage, device_usage, co2_grams)
        )
    
    def get_user_activity_logs(self, user_id: int, limit: int = None) -> List[Dict]:
        """Get all activity logs for a user"""
        if limit:
            query = """
                SELECT * FROM activity_logs 
                WHERE user_id = %s 
                ORDER BY log_date DESC 
                LIMIT %s
            """
            results = self.execute_query(query, (user_id, limit))
        else:
            query = """
                SELECT * FROM activity_logs 
                WHERE user_id = %s 
                ORDER BY log_date DESC
            """
            results = self.execute_query(query, (user_id,))
        
        # Convert to list of dicts and handle date conversion
        logs = []
        for row in results:
            log = dict(row)
            log['date'] = log.pop('log_date').strftime('%Y-%m-%d')
            log['emails'] = int(log['emails'])
            log['video_calls'] = float(log['video_calls'])
            log['streaming'] = float(log['streaming'])
            log['cloud_storage'] = float(log['cloud_storage'])
            log['device_usage'] = float(log['device_usage'])
            log['co2_grams'] = float(log['co2_grams'])
            logs.append(log)
        
        return logs
    
    def get_activity_logs_by_date_range(self, user_id: int, start_date: date, end_date: date) -> List[Dict]:
        """Get activity logs within a date range"""
        query = """
            SELECT * FROM activity_logs 
            WHERE user_id = %s AND log_date BETWEEN %s AND %s
            ORDER BY log_date DESC
        """
        results = self.execute_query(query, (user_id, start_date, end_date))
        
        logs = []
        for row in results:
            log = dict(row)
            log['date'] = log.pop('log_date').strftime('%Y-%m-%d')
            log['emails'] = int(log['emails'])
            log['video_calls'] = float(log['video_calls'])
            log['streaming'] = float(log['streaming'])
            log['cloud_storage'] = float(log['cloud_storage'])
            log['device_usage'] = float(log['device_usage'])
            log['co2_grams'] = float(log['co2_grams'])
            logs.append(log)
        
        return logs
    
    # Badge operations
    def award_badge(self, user_id: int, badge_name: str) -> bool:
        """Award a badge to a user (idempotent - won't duplicate)"""
        query = """
            INSERT INTO user_badges (user_id, badge_name, earned_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, badge_name) DO NOTHING
            RETURNING id
        """
        result = self.execute_insert(query, (user_id, badge_name, date.today()))
        return result is not None
    
    def get_user_badges(self, user_id: int) -> List[str]:
        """Get list of badge names earned by user"""
        query = """
            SELECT badge_name FROM user_badges 
            WHERE user_id = %s 
            ORDER BY earned_date DESC
        """
        results = self.execute_query(query, (user_id,))
        return [row['badge_name'] for row in results]
    
    def get_recently_earned_badges(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get badges earned in the last N days"""
        query = """
            SELECT badge_name, earned_date 
            FROM user_badges 
            WHERE user_id = %s AND earned_date >= CURRENT_DATE - (INTERVAL '1 day' * %s)
            ORDER BY earned_date DESC
        """
        results = self.execute_query(query, (user_id, days))
        return [dict(row) for row in results]
    
    # Statistics and analytics
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a user"""
        query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(co2_grams) as total_co2,
                AVG(co2_grams) as avg_daily_co2,
                MIN(co2_grams) as best_day_co2,
                MAX(co2_grams) as worst_day_co2
            FROM activity_logs
            WHERE user_id = %s
        """
        results = self.execute_query(query, (user_id,))
        if results and results[0]['total_days']:
            stats = dict(results[0])
            # Convert to float/int
            stats['total_days'] = int(stats['total_days'])
            stats['total_co2'] = float(stats['total_co2']) if stats['total_co2'] else 0
            stats['avg_daily_co2'] = float(stats['avg_daily_co2']) if stats['avg_daily_co2'] else 0
            stats['best_day_co2'] = float(stats['best_day_co2']) if stats['best_day_co2'] else 0
            stats['worst_day_co2'] = float(stats['worst_day_co2']) if stats['worst_day_co2'] else 0
            return stats
        return {
            'total_days': 0,
            'total_co2': 0,
            'avg_daily_co2': 0,
            'best_day_co2': 0,
            'worst_day_co2': 0
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by total score for leaderboard"""
        query = """
            SELECT 
                username,
                current_level,
                total_score,
                (SELECT COUNT(*) FROM activity_logs WHERE user_id = users.id) as days_tracked,
                (SELECT AVG(co2_grams) FROM activity_logs WHERE user_id = users.id) as avg_co2
            FROM users
            ORDER BY total_score DESC
            LIMIT %s
        """
        results = self.execute_query(query, (limit,))
        return [dict(row) for row in results]
    
    def delete_user_data(self, user_id: int):
        """Delete all user data (for reset functionality)"""
        queries = [
            "DELETE FROM user_badges WHERE user_id = %s",
            "DELETE FROM activity_logs WHERE user_id = %s",
            "UPDATE users SET total_score = 0, current_level = 'Bronze' WHERE id = %s"
        ]
        for query in queries:
            self.execute_query(query, (user_id,), fetch=False)
