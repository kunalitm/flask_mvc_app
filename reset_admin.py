"""
Simple script to reset admin user without imports
"""
import sqlite3
import bcrypt
from pathlib import Path
import sys

# Set stdout encoding to utf-8 to handle special characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Database path
db_path = Path('instance/app.db')

if not db_path.exists():
    print("ERROR: Database not found at instance/app.db")
    print("Please run 'python run.py' first to create the database")
    exit(1)

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if admin exists
cursor.execute("SELECT id, username, password_hash, is_active FROM users WHERE username = 'admin'")
admin = cursor.fetchone()

if admin:
    admin_id, username, old_hash, is_active = admin
    print(f"\nFound admin user (ID: {admin_id})")
    print(f"  Username: {username}")
    print(f"  Active: {bool(is_active)}")

    # Generate new password hash
    new_password = 'admin123'
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update password
    cursor.execute("""
        UPDATE users
        SET password_hash = ?, is_active = 1
        WHERE id = ?
    """, (password_hash, admin_id))
    conn.commit()

    print(f"\n✓ Password reset successfully!")
    print(f"  New password: {new_password}")

else:
    print("\nAdmin user not found. Creating...")

    # Get admin role ID
    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
    role_result = cursor.fetchone()

    if not role_result:
        print("ERROR: Admin role not found. Database may not be initialized.")
        print("Please run 'python run.py' first")
        conn.close()
        exit(1)

    admin_role_id = role_result[0]

    # Create admin user
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, first_name, last_name, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('admin', 'admin@example.com', password_hash, 'System', 'Administrator', 1))

    admin_id = cursor.lastrowid

    # Assign admin role
    cursor.execute("""
        INSERT INTO user_roles (user_id, role_id)
        VALUES (?, ?)
    """, (admin_id, admin_role_id))

    conn.commit()
    print("\n✓ Admin user created successfully!")

conn.close()

print("\n" + "=" * 50)
print("You can now login with:")
print("  Username: admin")
print("  Password: admin123")
print("=" * 50)
print("\nPlease restart the Flask server if it's running.")
