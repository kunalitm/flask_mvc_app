"""
Check database tables and contents

This script connects to the database using the application configuration
and displays all tables with row counts.

Supports SQLite and PostgreSQL databases.

Usage:
    python check_db.py [--env {development,production,testing}]
    python check_db.py --uri <database_uri>

Examples:
    python check_db.py                    # Use development config (default)
    python check_db.py --env production   # Use production config
    python check_db.py --uri "postgresql://user:pass@localhost/dbname"
"""
import sys
import os
import argparse
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import config


def get_db_type_from_uri(database_uri):
    """
    Determine database type from URI

    Args:
        database_uri: SQLAlchemy database URI

    Returns:
        Tuple of (db_type, connection_info)
        db_type: 'sqlite', 'postgresql', 'mysql', etc., or None
        connection_info: Path for SQLite, parsed URI for others
    """
    if not database_uri:
        return None, None

    parsed = urlparse(database_uri)
    db_type = parsed.scheme

    # Handle SQLite special cases
    if database_uri == 'sqlite:///:memory:':
        print("\n[INFO] Database is in-memory (testing mode).")
        print("In-memory databases are temporary and cannot be inspected externally.")
        print("They are created and destroyed with each test run.")
        return None, None
    elif database_uri.startswith('sqlite:///'):
        # Remove 'sqlite:///' prefix to get the path
        db_path = database_uri.replace('sqlite:///', '', 1)
        return 'sqlite', Path(db_path)
    elif db_type in ('postgresql', 'postgres'):
        return 'postgresql', parsed
    elif db_type == 'mysql':
        return 'mysql', parsed
    else:
        print(f"\n[WARNING] Database type '{db_type}' detected.")
        print("This script currently supports SQLite and PostgreSQL databases.")
        print("MySQL and other databases have limited support.")
        return db_type, parsed


def check_sqlite_database(db_path):
    """Check SQLite database"""
    import sqlite3

    if not db_path.exists():
        print("\n[ERROR] Database file doesn't exist!")
        print("\nTo create the database, run:")
        print("  python init_database.py")
        return False

    print(f"Database Path: {db_path}")
    print(f"Database Size: {db_path.stat().st_size:,} bytes")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        if not tables:
            print("\n[WARNING] No tables found in database!")
            print("\nTo initialize the database, run:")
            print("  python init_database.py")
            conn.close()
            return True

        print(f"\n[INFO] Found {len(tables)} table(s)")
        print("\nTables in database:")
        print("-" * 60)

        total_rows = 0
        for table in tables:
            table_name = table[0]

            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count

            # Get column count
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_count = len(columns)

            print(f"\n  [{table_name}]")
            print(f"    Rows: {count}")
            print(f"    Columns: {col_count}")

            # Show column names
            col_names = [col[1] for col in columns]
            print(f"    Fields: {', '.join(col_names)}")

        print("\n" + "-" * 60)
        print(f"Total rows across all tables: {total_rows}")
        print("=" * 60 + "\n")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False


def check_postgresql_database(parsed_uri):
    """Check PostgreSQL database"""
    try:
        import psycopg2
    except ImportError:
        print("\n[ERROR] psycopg2 is not installed!")
        print("\nTo use PostgreSQL, install it with:")
        print("  pip install psycopg2-binary")
        return False

    # Extract connection parameters
    hostname = parsed_uri.hostname or 'localhost'
    port = parsed_uri.port or 5432
    username = parsed_uri.username
    password = parsed_uri.password
    database = parsed_uri.path.lstrip('/')

    print(f"Database Host: {hostname}:{port}")
    print(f"Database Name: {database}")
    print(f"Username: {username}")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # Get database size
        cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{database}'))")
        db_size = cursor.fetchone()[0]
        print(f"Database Size: {db_size}")

        # Get all tables from public schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        if not tables:
            print("\n[WARNING] No tables found in public schema!")
            conn.close()
            return True

        print(f"\n[INFO] Found {len(tables)} table(s) in public schema")
        print("\nTables in database:")
        print("-" * 60)

        total_rows = 0
        for table in tables:
            table_name = table[0]

            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count

            # Get column information
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cursor.fetchall()
            col_count = len(columns)

            print(f"\n  [{table_name}]")
            print(f"    Rows: {count}")
            print(f"    Columns: {col_count}")

            # Show column names
            col_names = [col[0] for col in columns]
            print(f"    Fields: {', '.join(col_names)}")

        print("\n" + "-" * 60)
        print(f"Total rows across all tables: {total_rows}")
        print("=" * 60 + "\n")

        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"\n[ERROR] PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Connection error: {e}")
        return False


def check_database(env='development', custom_uri=None):
    """
    Check database tables and row counts

    Args:
        env: Environment name (development, production, testing)
        custom_uri: Custom database URI (overrides environment config)
    """
    # Get database URI
    if custom_uri:
        database_uri = custom_uri
        env_display = f"Custom URI"
    else:
        # Get configuration for the specified environment
        config_class = config.get(env, config['default'])
        database_uri = config_class.SQLALCHEMY_DATABASE_URI
        env_display = env

    print("\n" + "="*60)
    print("  Database Inspection Tool")
    print("="*60)
    print(f"\nEnvironment: {env_display}")
    print(f"Database URI: {database_uri}")

    # Determine database type and get connection info
    db_type, connection_info = get_db_type_from_uri(database_uri)

    if db_type is None:
        sys.exit(0)  # Exit gracefully for unsupported database types

    # Check database based on type
    if db_type == 'sqlite':
        success = check_sqlite_database(connection_info)
    elif db_type == 'postgresql':
        success = check_postgresql_database(connection_info)
    else:
        print(f"\n[ERROR] Database type '{db_type}' is not fully supported.")
        success = False

    sys.exit(0 if success else 1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Check database tables and contents (supports SQLite and PostgreSQL)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--env',
        default='development',
        choices=['development', 'production', 'testing'],
        help='Environment to use (default: development)'
    )
    parser.add_argument(
        '--uri',
        help='Custom database URI (overrides --env). Example: postgresql://user:pass@localhost/dbname'
    )

    args = parser.parse_args()

    # Use custom URI if provided, otherwise use environment config
    if args.uri:
        check_database(custom_uri=args.uri)
    else:
        # Use FLASK_ENV from environment if set, otherwise use command-line arg
        env = os.environ.get('FLASK_ENV', args.env)

        # Also check for DATABASE_URL environment variable
        custom_uri = os.environ.get('DATABASE_URL')
        if custom_uri:
            print(f"[INFO] Using DATABASE_URL from environment")
            check_database(custom_uri=custom_uri)
        else:
            check_database(env)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
