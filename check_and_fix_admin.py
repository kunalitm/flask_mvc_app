"""
Script to check and fix admin user login
"""
from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.config.settings import config

# Create app instance
app = create_app(config['development'])

with app.app_context():
    print("Checking database...")

    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()

    if admin:
        print(f"\n✓ Admin user found:")
        print(f"  - Username: {admin.username}")
        print(f"  - Email: {admin.email}")
        print(f"  - Active: {admin.is_active}")
        print(f"  - Roles: {[role.name for role in admin.roles]}")

        # Test password
        print("\n Testing password 'admin123'...")
        if admin.check_password('admin123'):
            print("  ✓ Password is correct!")
        else:
            print("  ✗ Password is incorrect. Resetting...")
            admin.set_password('admin123')
            db.session.commit()
            print("  ✓ Password has been reset to 'admin123'")

        # Make sure user is active
        if not admin.is_active:
            print("\n  Activating admin user...")
            admin.is_active = True
            db.session.commit()
            print("  ✓ Admin user is now active")

        # Check roles
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role and not admin.has_role('admin'):
            print("\n  Adding admin role...")
            admin.add_role(admin_role)
            db.session.commit()
            print("  ✓ Admin role added")

    else:
        print("\n✗ Admin user not found. Creating...")

        # Get or create admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("  Creating admin role...")
            import json
            admin_role = Role(
                name='admin',
                description='Administrator with full system access',
                permissions=json.dumps(['users.*', 'roles.*', 'plugins.*', '*']),
                is_system=True
            )
            db.session.add(admin_role)
            db.session.commit()

        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        admin.add_role(admin_role)
        db.session.add(admin)
        db.session.commit()

        print("\n✓ Admin user created successfully!")
        print("  - Username: admin")
        print("  - Password: admin123")

    print("\n" + "="*50)
    print("You can now login with:")
    print("  Username: admin")
    print("  Password: admin123")
    print("="*50)
