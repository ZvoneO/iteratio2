"""
Configuration settings for the Resource Planning Application.
Different configurations for development, testing, and production environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Upload folder for files
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    @staticmethod
    def get_database_url():
        """
        Get database URL from environment and fix it if needed.
        Render provides PostgreSQL URLs starting with postgres://, but SQLAlchemy requires postgresql://
        """
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        # Fix for Render PostgreSQL URLs
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

class DevelopmentConfig(Config):
    """Development configuration with debugging enabled."""
    DEBUG = True
    
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = self.get_database_url()

class TestingConfig(Config):
    """Testing configuration with testing database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration with secure settings."""
    DEBUG = False
    
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = self.get_database_url()
        # In production, ensure SECRET_KEY is set in environment
        # If not set, use the default from Config class as a fallback
        if os.environ.get('SECRET_KEY'):
            self.SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Enable HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig(),
    'testing': TestingConfig(),
    'production': ProductionConfig(),
    'default': DevelopmentConfig()
}
