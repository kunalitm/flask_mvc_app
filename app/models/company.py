"""
Company model for multi-tenant architecture
"""
from datetime import datetime
from app import db


class Company(db.Model):
    """Company model for multi-tenancy"""

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    # Contact information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

    # Settings
    max_users = db.Column(db.Integer, default=10)
    settings = db.Column(db.JSON, default=dict)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', back_populates='company', lazy='dynamic')
    company_plugins = db.relationship('CompanyPlugin', back_populates='company', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'

    def to_dict(self, include_stats=False):
        """Convert company to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'is_active': self.is_active,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'max_users': self.max_users,
            'settings': self.settings or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_stats:
            data['user_count'] = self.users.count()
            data['plugin_count'] = self.company_plugins.filter_by(is_enabled=True).count()

        return data

    def get_enabled_plugins(self):
        """Get list of enabled plugins for this company"""
        return [cp.plugin for cp in self.company_plugins.filter_by(is_enabled=True)]

    def has_plugin(self, plugin_id):
        """Check if company has a specific plugin enabled"""
        return self.company_plugins.filter_by(
            plugin_id=plugin_id,
            is_enabled=True
        ).first() is not None

    def can_add_user(self):
        """Check if company can add more users"""
        return self.users.count() < self.max_users
