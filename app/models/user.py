"""
User model for authentication and authorization
"""
from datetime import datetime
from app import db, bcrypt


class User(db.Model):
    """User model with authentication support"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', back_populates='users', lazy='dynamic')

    def __init__(self, username, email, password, first_name=None, last_name=None):
        """Initialize user with hashed password"""
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.roles.filter_by(name=role_name).first() is not None

    def has_any_role(self, role_names):
        """Check if user has any of the specified roles"""
        return any(self.has_role(role) for role in role_names)

    def add_role(self, role):
        """Add a role to the user"""
        if not self.has_role(role.name):
            self.roles.append(role)

    def remove_role(self, role):
        """Remove a role from the user"""
        if self.has_role(role.name):
            self.roles.remove(role)

    def to_dict(self, include_roles=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_roles:
            data['roles'] = [role.to_dict() for role in self.roles]
        return data

    def __repr__(self):
        return f'<User {self.username}>'
