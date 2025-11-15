"""
Role model for role-based access control
"""
from datetime import datetime
from app import db


class Role(db.Model):
    """Role model for RBAC"""

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string of permissions
    is_system = db.Column(db.Boolean, default=False)  # System roles cannot be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', secondary='user_roles', back_populates='roles', lazy='dynamic')

    def __init__(self, name, description=None, permissions=None, is_system=False):
        """Initialize role"""
        self.name = name
        self.description = description
        self.permissions = permissions or '[]'
        self.is_system = is_system

    def to_dict(self, include_users=False):
        """Convert role to dictionary"""
        import json
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': json.loads(self.permissions) if self.permissions else [],
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_users:
            data['user_count'] = self.users.count()
        return data

    def __repr__(self):
        return f'<Role {self.name}>'
