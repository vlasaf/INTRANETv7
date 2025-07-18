"""
Session management for HEXACO test progress tracking.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time

# Используем абсолютный импорт
from hexaco_bot.src.data.database import DatabaseManager

logger = logging.getLogger(__name__)

class UserSession:
    """Represents a user test session."""
    
    def __init__(self, session_id: str, user_id: int, status: str = 'active'):
        self.session_id = session_id
        self.user_id = user_id
        self.status = status # active, completed, abandoned
        self.current_test_type = 'hexaco'  # hexaco, sds, svs
        self.current_question = 1 # Current question number for the active test
        self.responses: Dict[str, Dict[int, Any]] = { # Store responses for each test type
            'hexaco': {},
            'sds': {},
            'svs': {},
            'panas': {},
            'self_efficacy': {},
            'cdrisc': {},
            'rfq': {},
            'pid5bfm': {}
        }
        self.test_completed: Dict[str, bool] = { # Track completion status for each test
            'hexaco': False,
            'sds': False,
            'svs': False,
            'panas': False,
            'self_efficacy': False,
            'cdrisc': False,
            'rfq': False,
            'pid5bfm': False
        }
        self.started_at = datetime.now()
        self.state = 'start'  # General state: start, registration_gender, registration_name, testing, menu, completed_all
        self.temp_data = {}  # Temporary data storage during registration

class SessionManager:
    """Manages user sessions and test progress."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.active_sessions: Dict[int, UserSession] = {}
        logger.info("Session manager initialized")
    
    def create_session(self, user_id: int) -> str:
        """Create new test session for user."""
        session_id = str(uuid.uuid4())
        
        # Create session in database
        if self.db.create_test_session(session_id, user_id):
            # Create in-memory session
            session = UserSession(session_id, user_id)
            self.active_sessions[user_id] = session
            logger.info(f"Session created for user {user_id}: {session_id}")
            return session_id
        else:
            logger.error(f"Failed to create session for user {user_id}")
            return None
    
    def get_session(self, user_id: int) -> Optional[UserSession]:
        """Get active session for user."""
        return self.active_sessions.get(user_id)
    
    def get_or_create_session(self, user_id: int) -> UserSession:
        """Get existing session or create new one."""
        session = self.get_session(user_id)
        if not session:
            session_id = self.create_session(user_id)
            if session_id:
                session = self.active_sessions[user_id]
        return session
    
    def update_session_state(self, user_id: int, state: str, temp_data: Dict = None):
        """Update session state and temporary data."""
        session = self.get_session(user_id)
        if session:
            session.state = state
            # Do not reset current_test_type if state is 'menu' or 'testing'
            # This allows to resume the correct test flow
            if temp_data:
                session.temp_data.update(temp_data)
            logger.debug(f"Session state updated for user {user_id}: {state}, current test: {session.current_test_type}")
    
    def save_response(self, user_id: int, test_type: str, question_num: int, response: Any) -> bool:
        """Save user response to question for a specific test."""
        session = self.get_session(user_id)
        if session and test_type in session.responses:
            session.responses[test_type][question_num] = response
            session.current_question = question_num + 1 # This should be specific to the test type
            
            # Database update might need to be more generic or handled at test completion
            # For now, let's assume progress is mainly in-memory until test completion
            # self.db.update_session_progress(session.session_id, session.current_question, test_type) # Example
            logger.info(f"Response saved for user {user_id}, test {test_type}, Q{question_num}: {response}")
            return True
        logger.warning(f"Failed to save response for user {user_id}, test {test_type}, Q{question_num}")
        return False
    
    def complete_test_part(self, user_id: int, test_type: str):
        """Mark a specific test part as completed for the user."""
        session = self.get_session(user_id)
        if session and test_type in session.test_completed:
            session.test_completed[test_type] = True
            session.current_question = 1 # Reset for the next test or if needed
            logger.info(f"Test part {test_type} completed for user {user_id}.")
            # Potentially update a general session status in DB if needed
            # self.db.update_session_status(session.session_id, f"{test_type}_completed")
        else:
            logger.warning(f"Could not mark test {test_type} as completed for user {user_id}.")

    def get_next_test(self, user_id: int) -> Optional[str]:
        """Determines the next test for the user."""
        session = self.get_session(user_id)
        if not session:
            return None
        
        if not session.test_completed['hexaco']:
            return 'hexaco'
        if not session.test_completed['sds']:
            return 'sds'
        if not session.test_completed['svs']:
            return 'svs'
        return None # All tests completed

    def complete_session(self, user_id: int) -> bool:
        """Mark session as completed (all tests done)."""
        session = self.get_session(user_id)
        if session:
            session.status = 'completed'
            session.state = 'completed'
            
            # Update database
            success = self.db.complete_session(session.session_id)
            if success:
                # Remove from active sessions
                del self.active_sessions[user_id]
                logger.info(f"Session completed for user {user_id}")
            return success
        return False
    
    def abandon_session(self, user_id: int) -> bool:
        """Mark session as abandoned."""
        session = self.get_session(user_id)
        if session:
            session.status = 'abandoned'
            
            # Update database (you might want to add this method to DatabaseManager)
            # For now, just remove from active sessions
            del self.active_sessions[user_id]
            logger.info(f"Session abandoned for user {user_id}")
            return True
        return False
    
    def get_session_progress(self, user_id: int) -> Dict[str, Any]:
        """Get session progress information."""
        session = self.get_session(user_id)
        if session:
            return {
                'session_id': session.session_id,
                'current_question': session.current_question,
                'total_questions': 100,
                'progress_percent': (session.current_question - 1) / 100 * 100,
                'responses_count': len(session.responses),
                'state': session.state,
                'started_at': session.started_at
            }
        return None
    
    def is_session_expired(self, user_id: int, timeout_hours: int = 24) -> bool:
        """Check if session has expired."""
        session = self.get_session(user_id)
        if session:
            expiry_time = session.started_at + timedelta(hours=timeout_hours)
            return datetime.now() > expiry_time
        return True
    
    def cleanup_expired_sessions(self, timeout_hours: int = 24):
        """Remove expired sessions from memory."""
        expired_users = []
        for user_id, session in self.active_sessions.items():
            if self.is_session_expired(user_id, timeout_hours):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.abandon_session(user_id)
            logger.info(f"Cleaned up expired session for user {user_id}")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions) 