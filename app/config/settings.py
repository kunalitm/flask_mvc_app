"""
Application configuration settings
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Base configuration"""

    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "instance" / "app.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Plugin configuration
    PLUGIN_DIR = BASE_DIR / 'app' / 'plugins'
    PLUGIN_CONFIG_DIR = BASE_DIR / 'instance' / 'plugin_configs'
    ENABLED_PLUGINS = []  # Will be populated from database

    # API configuration
    API_TITLE = 'Flask MVC Plugin API'
    API_VERSION = 'v1'

    # RBAC configuration
    DEFAULT_ROLES = ['admin', 'user', 'guest']

    # Pagination
    ITEMS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create instance directories if they don't exist
        os.makedirs(app.config['PLUGIN_CONFIG_DIR'], exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
