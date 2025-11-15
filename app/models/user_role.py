"""
User-Role association table for many-to-many relationship
"""
from datetime import datetime
from app import db


class UserRole(db.Model):
    """Association table for User-Role many-to-many relationship"""

    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )

    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'
