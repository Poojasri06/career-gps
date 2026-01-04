"""
User Authentication Service
Handles user registration, login, and session management
"""
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

class UserAuth:
    def __init__(self, users_file='data/users.json'):
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist"""
        Path(self.users_file).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register_user(self, email, password, name, user_type='student'):
        """
        Register a new user
        Returns: (success: bool, message: str)
        """
        users = self._load_users()
        
        # Check if user already exists
        if email in users:
            return False, "Email already registered"
        
        # Create new user
        users[email] = {
            'name': name,
            'password': self._hash_password(password),
            'user_type': user_type,
            'created_at': datetime.now().isoformat(),
            'preferences': {
                'email_notifications': True,
                'notification_time': '09:00'
            },
            'profile': None,
            'career_history': [],
            'learning_progress': {}
        }
        
        self._save_users(users)
        return True, "Registration successful"
    
    def login_user(self, email, password):
        """
        Authenticate user
        Returns: (success: bool, user_data: dict or None, message: str)
        """
        users = self._load_users()
        
        if email not in users:
            return False, None, "Email not found"
        
        if users[email]['password'] != self._hash_password(password):
            return False, None, "Incorrect password"
        
        # Return user data without password
        user_data = users[email].copy()
        user_data.pop('password')
        user_data['email'] = email
        
        return True, user_data, "Login successful"
    
    def update_user_profile(self, email, profile_data):
        """Update user's career profile"""
        users = self._load_users()
        
        if email not in users:
            return False, "User not found"
        
        users[email]['profile'] = profile_data
        users[email]['profile']['updated_at'] = datetime.now().isoformat()
        
        self._save_users(users)
        return True, "Profile updated"
    
    def update_learning_progress(self, email, skill, progress):
        """Update user's learning progress for a skill"""
        users = self._load_users()
        
        if email not in users:
            return False, "User not found"
        
        if 'learning_progress' not in users[email]:
            users[email]['learning_progress'] = {}
        
        users[email]['learning_progress'][skill] = {
            'progress': progress,
            'updated_at': datetime.now().isoformat()
        }
        
        self._save_users(users)
        return True, "Progress updated"
    
    def add_career_history(self, email, career_data):
        """Add a career decision to user's history"""
        users = self._load_users()
        
        if email not in users:
            return False, "User not found"
        
        career_entry = {
            'timestamp': datetime.now().isoformat(),
            'career': career_data
        }
        
        users[email]['career_history'].append(career_entry)
        self._save_users(users)
        return True, "Career history updated"
    
    def get_user_data(self, email):
        """Get full user data"""
        users = self._load_users()
        
        if email not in users:
            return None
        
        user_data = users[email].copy()
        user_data.pop('password', None)
        user_data['email'] = email
        
        return user_data
    
    def update_notification_preferences(self, email, preferences):
        """Update user's notification preferences"""
        users = self._load_users()
        
        if email not in users:
            return False, "User not found"
        
        users[email]['preferences'].update(preferences)
        self._save_users(users)
        return True, "Preferences updated"
