"""
Database access layer for HEXACO bot.
Handles SQLite database operations and schema management.
"""

import sqlite3
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from hexaco_bot.config.settings import DATABASE_PATH
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for HEXACO bot."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database manager with path."""
        self.db_path = db_path
        self._ensure_database_directory()
        
    def _ensure_database_directory(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def initialize_database(self) -> bool:
        """Initialize database with required tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
                        paei_index TEXT,
                        mbti_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        overall_completion_status_set_at TIMESTAMP DEFAULT NULL
                    )
                ''')
                
                # Create test_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'abandoned')),
                        current_question INTEGER DEFAULT 1,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Create results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS results (
                        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        test_type TEXT NOT NULL CHECK (test_type IN ('hexaco', 'sds', 'svs', 'panas', 'self_efficacy', 'cdrisc', 'rfq', 'pid5bfm')),
                        honesty_humility REAL,
                        emotionality REAL,
                        extraversion REAL,
                        agreeableness REAL,
                        conscientiousness REAL,
                        openness REAL,
                        altruism REAL,
                        self_contact REAL,
                        choiceful_action REAL,
                        sds_index REAL,
                        scores_json TEXT,
                        responses TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES test_sessions (session_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_user_id ON users (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON test_sessions (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_status ON test_sessions (status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_user_id ON results (user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_session_id ON results (session_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def create_user(self, user_id: int, username: Optional[str], 
                   first_name: str, last_name: str, gender: str) -> bool:
        """Create new user record."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, gender, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name, gender))
                conn.commit()
                logger.info(f"User created/updated: {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def create_test_session(self, session_id: str, user_id: int) -> bool:
        """Create new test session."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_sessions (session_id, user_id, status)
                    VALUES (?, ?, 'active')
                ''', (session_id, user_id))
                conn.commit()
                logger.info(f"Test session created: {session_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    def update_session_progress(self, session_id: str, current_question: int) -> bool:
        """Update session progress."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE test_sessions 
                    SET current_question = ? 
                    WHERE session_id = ?
                ''', (current_question, session_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update session progress {session_id}: {e}")
            return False
    
    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE test_sessions 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (session_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to complete session {session_id}: {e}")
            return False
    
    def save_test_result(self, session_id: str, user_id: int, test_type: str,
                           scores: Dict[str, Any], responses_json: str) -> bool:
        """Save results for a specific test type."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data based on test_type
                data = {
                    'session_id': session_id,
                    'user_id': user_id,
                    'test_type': test_type,
                    'responses': responses_json,
                    'scores_json': json.dumps(scores) # Store all scores as JSON for flexibility
                }
                
                # Add specific columns if they exist in scores, otherwise NULL
                # HEXACO
                data['honesty_humility'] = scores.get('honesty_humility', scores.get('H'))
                data['emotionality'] = scores.get('emotionality', scores.get('E'))
                data['extraversion'] = scores.get('extraversion', scores.get('X'))
                data['agreeableness'] = scores.get('agreeableness', scores.get('A'))
                data['conscientiousness'] = scores.get('conscientiousness', scores.get('C'))
                data['openness'] = scores.get('openness', scores.get('O'))
                data['altruism'] = scores.get('altruism', scores.get('Alt'))
                # SDS
                data['self_contact'] = scores.get('self_contact')
                data['choiceful_action'] = scores.get('choiceful_action')
                data['sds_index'] = scores.get('sds_index')
                
                # Construct query dynamically (safer with placeholders)
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                sql = f"INSERT INTO results ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, tuple(data.values()))
                conn.commit()
                logger.info(f"Results for test {test_type} saved for session {session_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save {test_type} results for session {session_id}: {e}")
            return False
    
    def get_user_test_results(self, user_id: int, test_type: str) -> List[Dict[str, Any]]:
        """Get all results for a specific test type for a user, ordered by most recent."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Assuming scores_json contains the primary scores for SDS/SVS for easier retrieval
                cursor.execute('''
                    SELECT *, scores_json FROM results 
                    WHERE user_id = ? AND test_type = ? 
                    ORDER BY created_at DESC
                ''', (user_id, test_type))
                rows = cursor.fetchall()
                # Parse scores_json back to dict if needed or return raw
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get {test_type} results for user {user_id}: {e}")
            return []

    def get_all_user_results(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all test results for a user, grouped by test_type."""
        all_results = {}
        for test_type in ['hexaco', 'sds', 'svs', 'panas', 'self_efficacy', 'cdrisc', 'rfq', 'pid5bfm']:
            all_results[test_type] = self.get_user_test_results(user_id, test_type)
        return all_results

    def get_user_results(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all HEXACO results for a user, ordered by most recent."""
        # This method might be legacy if get_user_test_results is the new standard.
        # For now, let it fetch HEXACO by default.
        return self.get_user_test_results(user_id, 'hexaco')

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM test_sessions WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def set_overall_completion_status(self, user_id: int) -> bool:
        """Set the overall completion status timestamp for a user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users
                    SET overall_completion_status_set_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                logger.info(f"Overall completion status set for user {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to set overall completion status for user {user_id}: {e}")
            return False

    def get_completed_tests_for_user(self, user_id: int) -> Dict[str, bool]:
        """
        Get precise information about which tests have been completed by the user.
        Returns a dictionary with test names as keys and completion status as values.
        """
        completed_tests = {
            'hexaco': False,
            'sds': False,
            'svs': False,
            'panas': False,
            'self_efficacy': False,
            'cdrisc': False,
            'rfq': False,
            'pid5bfm': False
        }
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Get all test types that have results for this user
                cursor.execute('''
                    SELECT DISTINCT test_type 
                    FROM results 
                    WHERE user_id = ?
                ''', (user_id,))
                rows = cursor.fetchall()
                
                for row in rows:
                    test_type = row['test_type']
                    if test_type in completed_tests:
                        completed_tests[test_type] = True
                
                logger.info(f"Completed tests for user {user_id}: {completed_tests}")
                return completed_tests
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get completed tests for user {user_id}: {e}")
            return completed_tests  # Return default (all False) on error

    def update_user_paei(self, user_id: int, paei_index: str) -> bool:
        """Update user's PAEI index."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET paei_index = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (paei_index, user_id))
                conn.commit()
                logger.info(f"PAEI index updated for user {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update PAEI index for user {user_id}: {e}")
            return False

    def update_user_mbti(self, user_id: int, mbti_type: str) -> bool:
        """Update user's MBTI type."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET mbti_type = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (mbti_type, user_id))
                conn.commit()
                logger.info(f"MBTI type updated for user {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update MBTI type for user {user_id}: {e}")
            return False

    def get_user_data_for_report(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get all user data and test results for reporting."""
        user_data = self.get_user(user_id)
        if not user_data:
            return None
        
        report_data = dict(user_data) # Make a mutable copy
        
        # Remove sensitive or unnecessary data from user_data if needed
        # For example, if 'created_at' or 'updated_at' for the user row itself isn't needed in the report
        # report_data.pop('created_at', None) 
        # report_data.pop('updated_at', None)


        test_results = {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT test_type, scores_json, responses, created_at 
                    FROM results 
                    WHERE user_id = ? 
                    ORDER BY test_type, created_at DESC
                ''', (user_id,))
                rows = cursor.fetchall()

                for row in rows:
                    test_type = row['test_type']
                    if test_type not in test_results:
                        test_results[test_type] = []
                    
                    result_entry = {
                        "scores": json.loads(row['scores_json']) if row['scores_json'] else None,
                        "responses": json.loads(row['responses']) if row['responses'] else None,
                        "completed_at": row['created_at'] # Assuming created_at of result is completion time
                    }
                    test_results[test_type].append(result_entry)
            
            report_data['tests'] = test_results
            return report_data
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get all results for user {user_id} for report: {e}")
            # Return user_data even if results fetching fails, or handle as per requirements
            report_data['tests'] = {} # or None, or an error message
            return report_data # Or return None if results are critical
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON for user {user_id} results: {e}")
            report_data['tests'] = {"error": "Failed to parse test results JSON."}
            return report_data 