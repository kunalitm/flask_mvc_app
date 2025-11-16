"""
Initialize multi-company database schema
This script should be run AFTER adding the new models
"""
import sqlite3
from pathlib import Path
import bcrypt

db_path = Path('instance/app.db')

if not db_path.exists():
    print("ERROR: Database not found. Run 'python run.py' first")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("Initializing multi-company schema...")
print("="*60)

# 1. Create companies table
print("\n1. Creating companies table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    max_users INTEGER DEFAULT 10,
    settings TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✓ Companies table created")

# 2. Create company_plugins table
print("\n2. Creating company_plugins table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS company_plugins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    plugin_id INTEGER NOT NULL,
    is_enabled BOOLEAN DEFAULT 0,
    config TEXT,  -- JSON
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enabled_at TIMESTAMP,
    disabled_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (plugin_id) REFERENCES plugins(id) ON DELETE CASCADE,
    UNIQUE (company_id, plugin_id)
)
""")
print("✓ Company_plugins table created")

# 3. Add new columns to users table
print("\n3. Updating users table...")
try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0")
    print("✓ Added is_super_admin column")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ is_super_admin column already exists")
    else:
        raise

try:
    cursor.execute("ALTER TABLE users ADD COLUMN company_id INTEGER REFERENCES companies(id)")
    print("✓ Added company_id column")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ company_id column already exists")
    else:
        raise

# 4. Create default company for existing users
print("\n4. Creating default company...")
cursor.execute("SELECT COUNT(*) FROM companies WHERE slug = 'default'")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO companies (name, slug, description, max_users, settings)
        VALUES ('Default Company', 'default', 'Default company for existing users', 100, '{}')
    """)
    print("✓ Default company created")
else:
    print("✓ Default company already exists")

# 5. Assign existing users to default company (except super admin)
print("\n5. Assigning existing users to default company...")
cursor.execute("SELECT id FROM companies WHERE slug = 'default'")
default_company_id = cursor.fetchone()[0]

cursor.execute("""
    UPDATE users
    SET company_id = ?
    WHERE company_id IS NULL AND is_super_admin = 0
""", (default_company_id,))
print(f"✓ Assigned {cursor.rowcount} users to default company")

# 6. Create super admin role if it doesn't exist
print("\n6. Creating super admin role...")
cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
super_admin_role = cursor.fetchone()

if not super_admin_role:
    import json
    permissions = json.dumps(["*"])
    cursor.execute("""
        INSERT INTO roles (name, description, permissions, is_system)
        VALUES ('super_admin', 'Super Administrator with full system access', ?, 1)
    """, (permissions,))
    super_admin_role_id = cursor.lastrowid
    print("✓ Super admin role created")
else:
    super_admin_role_id = super_admin_role[0]
    print("✓ Super admin role already exists")

# 7. Create super admin user if it doesn't exist
print("\n7. Creating super admin user...")
cursor.execute("SELECT id FROM users WHERE username = 'superadmin'")
super_admin_user = cursor.fetchone()

if not super_admin_user:
    password_hash = bcrypt.hashpw('superadmin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_super_admin, company_id)
        VALUES ('superadmin', 'superadmin@system.local', ?, 'Super', 'Admin', 1, 1, NULL)
    """, (password_hash,))

    super_admin_user_id = cursor.lastrowid

    # Assign super admin role
    cursor.execute("""
        INSERT INTO user_roles (user_id, role_id)
        VALUES (?, ?)
    """, (super_admin_user_id, super_admin_role_id))

    print("✓ Super admin user created")
    print(f"   Username: superadmin")
    print(f"   Password: superadmin123")
else:
    print("✓ Super admin user already exists")

# 8. Update admin user permissions if needed
print("\n8. Updating admin role permissions...")
import json
admin_permissions = json.dumps([
    "users.*",
    "roles.*",
    "plugins.read",
    "plugins.update"
])
cursor.execute("""
    UPDATE roles
    SET permissions = ?
    WHERE name = 'admin' AND is_system = 1
""", (admin_permissions,))
print("✓ Admin role permissions updated")

# 9. Create company admin role
print("\n9. Creating company admin role...")
cursor.execute("SELECT id FROM roles WHERE name = 'company_admin'")
if not cursor.fetchone():
    company_admin_permissions = json.dumps([
        "users.create",
        "users.read",
        "users.update",
        "users.delete",
        "roles.read",
        "companies.read"
    ])
    cursor.execute("""
        INSERT INTO roles (name, description, permissions, is_system)
        VALUES ('company_admin', 'Company administrator with user management permissions', ?, 0)
    """, (company_admin_permissions,))
    print("✓ Company admin role created")
else:
    print("✓ Company admin role already exists")

conn.commit()
conn.close()

print("\n" + "="*60)
print("✓ Multi-company initialization complete!")
print("="*60)
print("\nSuper Admin Credentials:")
print("  Username: superadmin")
print("  Password: superadmin123")
print("\nYou can now:")
print("  1. Login as super admin")
print("  2. Create companies")
print("  3. Create company users")
print("  4. Install plugins to companies")
print("\nSee MULTI_COMPANY_GUIDE.md for detailed documentation")
