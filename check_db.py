"""Check database tables"""
import sqlite3
from pathlib import Path

db_path = Path('instance/app.db')

if not db_path.exists():
    print("Database file doesn't exist!")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"    Rows: {count}")

conn.close()
