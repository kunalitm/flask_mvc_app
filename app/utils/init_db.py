"""
Database initialization utilities
"""
import json
from app import db
from app.models.user import User
from app.models.role import Role
from app.models.company import Company
from app.models.plugin import Plugin
from app.models.company_plugin import CompanyPlugin


def initialize_database():
    """
    Initialize database with default roles, companies, plugins, and admin user.
    This function is idempotent - safe to run multiple times.
    """
    print("\n=== Starting Database Initialization ===\n")

    # Step 1: Initialize default roles
    _initialize_roles()

    # Step 2: Initialize default company
    _initialize_companies()

    # Step 3: Initialize default plugins
    _initialize_plugins()

    # Step 4: Initialize admin user
    _initialize_admin_user()

    print("\n=== Database Initialization Complete ===\n")


def _initialize_roles():
    """Initialize default system roles"""
    # Check if roles already exist
    if Role.query.count() > 0:
        print("[OK] Roles already initialized")
        return

    print("[INFO] Creating default roles...")

    # Create default roles
    admin_role = Role(
        name='admin',
        description='Administrator with full system access',
        permissions=json.dumps([
            'users.*',
            'roles.*',
            'plugins.*',
            'companies.*',
            '*'
        ]),
        is_system=True
    )

    manager_role = Role(
        name='manager',
        description='Manager with company-level access',
        permissions=json.dumps([
            'users.read',
            'users.create',
            'users.update',
            'companies.read',
            'companies.update',
            'plugins.read',
            'plugins.manage'
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
    db.session.add(manager_role)
    db.session.add(user_role)
    db.session.add(guest_role)
    db.session.commit()

    print(f"[OK] Created {Role.query.count()} default roles: admin, manager, user, guest")


def _initialize_companies():
    """Initialize default companies"""
    # Check if companies already exist
    if Company.query.count() > 0:
        print("[OK] Companies already initialized")
        return

    print("[INFO] Creating default companies...")

    # Create default demo company
    demo_company = Company(
        name='Demo Company',
        slug='demo-company',
        description='Default demo company for testing and development',
        is_active=True,
        email='demo@example.com',
        phone='+1-555-0100',
        address='123 Demo Street, Demo City, DC 12345',
        max_users=50,
        settings={
            'timezone': 'UTC',
            'currency': 'USD',
            'language': 'en'
        }
    )

    # Create another example company
    acme_company = Company(
        name='ACME Corporation',
        slug='acme-corp',
        description='ACME Corporation - Example company',
        is_active=True,
        email='contact@acme.example.com',
        phone='+1-555-0200',
        address='456 Business Ave, Corporate City, CC 67890',
        max_users=100,
        settings={
            'timezone': 'America/New_York',
            'currency': 'USD',
            'language': 'en'
        }
    )

    db.session.add(demo_company)
    db.session.add(acme_company)
    db.session.commit()

    print(f"[OK] Created {Company.query.count()} default companies")


def _initialize_plugins():
    """Initialize default plugins"""
    # Check if plugins already exist
    if Plugin.query.count() > 0:
        print("[OK] Plugins already initialized")
        return

    print("[INFO] Creating default plugins...")

    # Create stock plugin entry
    stock_plugin = Plugin(
        name='stock_plugin',
        version='1.0.0',
        description='Stock inventory management plugin with CRUD operations',
        author='System',
        is_enabled=True,
        is_system=True,
        config={
            'default_currency': 'USD',
            'enable_barcode': True,
            'low_stock_threshold': 10
        }
    )
    stock_plugin.enable()

    db.session.add(stock_plugin)
    db.session.commit()

    # Associate plugins with companies
    companies = Company.query.all()
    for company in companies:
        company_plugin = CompanyPlugin(
            company_id=company.id,
            plugin_id=stock_plugin.id,
            is_enabled=True,
            config={
                'warehouse_location': f'{company.name} Warehouse',
                'notification_email': company.email
            }
        )
        company_plugin.enable()
        db.session.add(company_plugin)

    db.session.commit()

    print(f"[OK] Created {Plugin.query.count()} default plugins")
    print(f"[OK] Enabled plugins for {len(companies)} companies")


def _initialize_admin_user():
    """Initialize default admin user"""
    # Create default admin user if no users exist
    if User.query.count() > 0:
        print("[OK] Admin user already exists")
        return

    print("[INFO] Creating default admin user...")

    admin_role = Role.query.filter_by(name='admin').first()
    demo_company = Company.query.filter_by(slug='demo-company').first()

    # Create super admin (no company assignment)
    super_admin = User(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='System',
        last_name='Administrator'
    )
    super_admin.is_super_admin = True
    super_admin.company_id = None  # Super admin has no company
    db.session.add(super_admin)
    db.session.flush()  # Flush to get the user ID
    super_admin.add_role(admin_role)

    # Create company admin for demo company
    if demo_company:
        manager_role = Role.query.filter_by(name='manager').first()
        if manager_role:
            company_admin = User(
                username='demo_admin',
                email='demo.admin@example.com',
                password='demo123',
                first_name='Demo',
                last_name='Admin'
            )
            company_admin.is_super_admin = False
            company_admin.company_id = demo_company.id
            db.session.add(company_admin)
            db.session.flush()  # Flush to get the user ID
            company_admin.add_role(manager_role)

        # Create regular user for demo company
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            regular_user = User(
                username='demo_user',
                email='demo.user@example.com',
                password='user123',
                first_name='Demo',
                last_name='User'
            )
            regular_user.is_super_admin = False
            regular_user.company_id = demo_company.id
            db.session.add(regular_user)
            db.session.flush()  # Flush to get the user ID
            regular_user.add_role(user_role)

    db.session.commit()

    print(f"[OK] Created {User.query.count()} default users")
    print("\n  Default credentials:")
    print("  +---------------------------------------------")
    print("  | Super Admin:")
    print("  |   Username: admin")
    print("  |   Password: admin123")
    print("  +---------------------------------------------")
    print("  | Demo Company Admin:")
    print("  |   Username: demo_admin")
    print("  |   Password: demo123")
    print("  +---------------------------------------------")
    print("  | Demo Company User:")
    print("  |   Username: demo_user")
    print("  |   Password: user123")
    print("  +---------------------------------------------")
    print("\n  [WARNING] Please change these passwords in production!")
