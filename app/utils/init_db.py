"""
Database initialization utilities
"""
import json
from app import db
from app.models.user import User
from app.models.role import Role


def initialize_database():
    """
    Initialize database with default roles and admin user
    """
    # Check if roles already exist
    if Role.query.count() > 0:
        return

    # Create default roles
    admin_role = Role(
        name='admin',
        description='Administrator with full system access',
        permissions=json.dumps([
            'users.*',
            'roles.*',
            'plugins.*',
            '*'
        ]),
        is_system=True
    )

    user_role = Role(
        name='user',
        description='Regular user with basic access',
        permissions=json.dumps([
            'users.read',
            'users.update_self'
        ]),
        is_system=True
    )

    guest_role = Role(
        name='guest',
        description='Guest user with limited access',
        permissions=json.dumps([
            'users.read'
        ]),
        is_system=True
    )

    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.add(guest_role)
    db.session.commit()

    # Create default admin user if no users exist
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        admin_user.add_role(admin_role)
        db.session.add(admin_user)
        db.session.commit()

        print("Default admin user created:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Please change this password in production!")
