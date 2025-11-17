"""
Standalone Database Initialization Script

This script initializes the database with default tables and data:
- Creates all database tables based on models
- Initializes default roles (admin, manager, user, guest)
- Creates default companies (Demo Company, ACME Corporation)
- Initializes default plugins (stock_plugin)
- Creates default users with different roles

Usage:
    python init_database.py [--force]

Options:
    --force     Force re-initialization (WARNING: This will drop all existing tables!)

Examples:
    python init_database.py              # Initialize if database doesn't exist
    python init_database.py --force      # Drop and recreate all tables
"""
import sys
import os
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.config.settings import config
from app.utils.init_db import initialize_database


def drop_all_tables(app):
    """Drop all database tables"""
    with app.app_context():
        print("\n[WARNING] Dropping all existing tables...")
        db.drop_all()
        print("[OK] All tables dropped")


def create_all_tables(app):
    """Create all database tables"""
    with app.app_context():
        print("\n[INFO] Creating database tables...")
        db.create_all()
        print("[OK] All tables created")


def check_database_exists():
    """Check if database file exists"""
    db_path = Path('instance/app.db')
    return db_path.exists()


def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(
        description='Initialize Flask MVC application database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-initialization (drops all existing tables)'
    )
    parser.add_argument(
        '--env',
        default='development',
        choices=['development', 'production', 'testing'],
        help='Environment to use (default: development)'
    )

    args = parser.parse_args()

    # Create Flask app (skip auto-initialization for manual control)
    env = os.environ.get('FLASK_ENV', args.env)
    os.environ['SKIP_DB_INIT'] = '1'  # Skip auto-initialization in create_app
    app = create_app(config.get(env, config['default']))

    print("\n" + "="*60)
    print("  Flask MVC App - Database Initialization")
    print("="*60)
    print(f"\nEnvironment: {env}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')}")

    # Check if database exists
    db_exists = check_database_exists()

    if args.force:
        if db_exists:
            response = input("\n[WARNING] This will DELETE ALL DATA. Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return

        drop_all_tables(app)
        create_all_tables(app)

        with app.app_context():
            initialize_database()

    elif not db_exists:
        print("\n[INFO] Database does not exist. Creating new database...")
        create_all_tables(app)

        with app.app_context():
            initialize_database()

    else:
        print("\n[OK] Database already exists.")
        print("\nOptions:")
        print("  1. Use --force flag to drop and recreate all tables")
        print("  2. The application will auto-initialize missing data on startup")

        response = input("\nWould you like to try initializing missing data now? (yes/no): ")
        if response.lower() == 'yes':
            with app.app_context():
                initialize_database()
        else:
            print("\nNo action taken.")

    print("\n" + "="*60)
    print("  Initialization Complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
