"""
Company-Plugin association model
"""
from datetime import datetime
from app import db


class CompanyPlugin(db.Model):
    """Association table for Company-Plugin relationship with additional metadata"""

    __tablename__ = 'company_plugins'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    plugin_id = db.Column(db.Integer, db.ForeignKey('plugins.id', ondelete='CASCADE'), nullable=False)

    # Plugin state for this company
    is_enabled = db.Column(db.Boolean, default=False)
    config = db.Column(db.JSON, default=dict)  # Company-specific plugin config

    # Timestamps
    installed_at = db.Column(db.DateTime, default=datetime.utcnow)
    enabled_at = db.Column(db.DateTime)
    disabled_at = db.Column(db.DateTime)

    # Relationships
    company = db.relationship('Company', back_populates='company_plugins')
    plugin = db.relationship('Plugin')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('company_id', 'plugin_id', name='unique_company_plugin'),
    )

    def __repr__(self):
        return f'<CompanyPlugin company={self.company_id} plugin={self.plugin_id}>'

    def enable(self):
        """Enable plugin for this company"""
        self.is_enabled = True
        self.enabled_at = datetime.utcnow()
        self.disabled_at = None

    def disable(self):
        """Disable plugin for this company"""
        self.is_enabled = False
        self.disabled_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'plugin_id': self.plugin_id,
            'plugin': self.plugin.to_dict() if self.plugin else None,
            'is_enabled': self.is_enabled,
            'config': self.config or {},
            'installed_at': self.installed_at.isoformat() if self.installed_at else None,
            'enabled_at': self.enabled_at.isoformat() if self.enabled_at else None,
            'disabled_at': self.disabled_at.isoformat() if self.disabled_at else None,
        }
