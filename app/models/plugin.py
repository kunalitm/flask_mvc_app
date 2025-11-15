"""
Plugin model for managing plugin state and configuration
"""
from datetime import datetime
from app import db
import json


class Plugin(db.Model):
    """Plugin model for tracking installed and enabled plugins"""

    __tablename__ = 'plugins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    version = db.Column(db.String(20))
    description = db.Column(db.String(500))
    author = db.Column(db.String(100))
    is_enabled = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)  # System plugins cannot be disabled
    config = db.Column(db.Text)  # JSON configuration
    install_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_enabled = db.Column(db.DateTime)
    last_disabled = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, version=None, description=None, author=None,
                 is_enabled=False, is_system=False, config=None):
        """Initialize plugin"""
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.is_enabled = is_enabled
        self.is_system = is_system
        self.config = json.dumps(config) if config else '{}'

    def get_config(self):
        """Get plugin configuration as dictionary"""
        return json.loads(self.config) if self.config else {}

    def set_config(self, config_dict):
        """Set plugin configuration from dictionary"""
        self.config = json.dumps(config_dict)

    def enable(self):
        """Enable the plugin"""
        self.is_enabled = True
        self.last_enabled = datetime.utcnow()

    def disable(self):
        """Disable the plugin"""
        if not self.is_system:
            self.is_enabled = False
            self.last_disabled = datetime.utcnow()

    def to_dict(self):
        """Convert plugin to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'is_enabled': self.is_enabled,
            'is_system': self.is_system,
            'config': self.get_config(),
            'install_date': self.install_date.isoformat() if self.install_date else None,
            'last_enabled': self.last_enabled.isoformat() if self.last_enabled else None,
            'last_disabled': self.last_disabled.isoformat() if self.last_disabled else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Plugin {self.name} ({"enabled" if self.is_enabled else "disabled"})>'
