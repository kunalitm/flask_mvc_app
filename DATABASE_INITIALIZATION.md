# Database Initialization Guide

This document explains how the database initialization works in the Flask MVC Plugin Application.

## Overview

The application provides automatic and manual database initialization with default tables and data. The initialization is idempotent, meaning it can be run multiple times safely without creating duplicate data.

## What Gets Initialized

### 1. Database Tables

All tables are created based on the SQLAlchemy models:

- `users` - User accounts with authentication
- `roles` - User roles for RBAC (Role-Based Access Control)
- `user_roles` - Many-to-many relationship between users and roles
- `companies` - Multi-tenant company data
- `plugins` - Plugin registry
- `company_plugins` - Plugin activation per company

### 2. Default Roles

Four system roles are created:

- **admin** - Administrator with full system access
  - Permissions: `users.*`, `roles.*`, `plugins.*`, `companies.*`, `*`

- **manager** - Manager with company-level access
  - Permissions: `users.read`, `users.create`, `users.update`, `companies.read`, `companies.update`, `plugins.read`, `plugins.manage`

- **user** - Regular user with basic access
  - Permissions: `users.read`, `users.update_self`

- **guest** - Guest user with limited access
  - Permissions: `users.read`

### 3. Default Companies

Two example companies are created:

- **Demo Company**
  - Slug: `demo-company`
  - Email: demo@example.com
  - Max Users: 50
  - Settings: UTC timezone, USD currency, English language

- **ACME Corporation**
  - Slug: `acme-corp`
  - Email: contact@acme.example.com
  - Max Users: 100
  - Settings: America/New_York timezone, USD currency, English language

### 4. Default Plugins

The stock inventory management plugin is initialized:

- **stock_plugin**
  - Version: 1.0.0
  - Description: Stock inventory management plugin with CRUD operations
  - Status: Enabled for all companies

### 5. Default Users

Three users are created with different roles:

- **Super Admin**
  - Username: `admin`
  - Password: `admin123`
  - Role: admin
  - Company: None (super admin has access to all companies)
  - Super Admin Flag: True

- **Demo Company Admin**
  - Username: `demo_admin`
  - Password: `demo123`
  - Role: manager
  - Company: Demo Company

- **Demo Company User**
  - Username: `demo_user`
  - Password: `user123`
  - Role: user
  - Company: Demo Company

**WARNING:** Please change these default passwords in production!

## Initialization Methods

### Method 1: Automatic Initialization (Default)

When you run the application normally, the database is automatically initialized:

```bash
python run.py
```

The application will:
1. Create all database tables if they don't exist
2. Initialize default data if tables are empty
3. Load and initialize plugins

### Method 2: Manual Initialization Script

Use the standalone initialization script for manual control:

```bash
# Initialize database if it doesn't exist
python init_database.py

# Force re-initialization (drops all existing tables)
python init_database.py --force

# Specify environment
python init_database.py --env production
```

#### Options

- `--force` - Force re-initialization by dropping all existing tables (WARNING: This deletes all data!)
- `--env {development,production,testing}` - Specify the environment (default: development)
- `-h, --help` - Show help message

#### Interactive Prompts

The script provides interactive prompts to prevent accidental data loss:

```
[WARNING] This will DELETE ALL DATA. Are you sure? (yes/no):
```

## File Structure

### Core Files

- [init_database.py](init_database.py) - Standalone database initialization script
- [app/utils/init_db.py](app/utils/init_db.py) - Database initialization utilities
- [app/__init__.py](app/__init__.py) - Application factory with auto-initialization
- [check_db.py](check_db.py) - Database inspection utility

### Models

- [app/models/user.py](app/models/user.py) - User model
- [app/models/role.py](app/models/role.py) - Role model
- [app/models/company.py](app/models/company.py) - Company model
- [app/models/plugin.py](app/models/plugin.py) - Plugin model
- [app/models/user_role.py](app/models/user_role.py) - User-Role association
- [app/models/company_plugin.py](app/models/company_plugin.py) - Company-Plugin association

## Checking Database Status

Use the `check_db.py` script to inspect the database. This script now reads the database connection string from the application configuration.

### Basic Usage

```bash
# Check development database (default)
python check_db.py

# Check production database
python check_db.py --env production

# Get help
python check_db.py --help
```

### Sample Output

```
============================================================
  Database Inspection Tool
============================================================

Environment: development
Database URI: sqlite:///C:\apps\repo\flask_mvc_app\instance\app.db
Database Path: C:\apps\repo\flask_mvc_app\instance\app.db
Database Size: 61,440 bytes

[INFO] Found 6 table(s)

Tables in database:
------------------------------------------------------------

  [companies]
    Rows: 2
    Columns: 12
    Fields: id, name, slug, description, is_active, email, phone, address, max_users, settings, created_at, updated_at

  [plugins]
    Rows: 1
    Columns: 13
    Fields: id, name, version, description, author, is_enabled, is_system, config, install_date, last_enabled, last_disabled, created_at, updated_at

  [roles]
    Rows: 4
    Columns: 7
    Fields: id, name, description, permissions, is_system, created_at, updated_at

  [users]
    Rows: 3
    Columns: 11
    Fields: id, username, email, password_hash, first_name, last_name, is_active, is_super_admin, company_id, created_at, updated_at

------------------------------------------------------------
Total rows across all tables: 15
============================================================
```

### Features

- **Environment-Aware**: Automatically uses the correct database based on the environment
- **Detailed Information**: Shows table names, row counts, column counts, and field names
- **Database Size**: Displays the database file size
- **Configuration-Based**: Reads connection string from `app.config.settings`
- **Error Handling**: Provides helpful error messages and suggestions

## Troubleshooting

### Issue: Database already exists

If the database already exists and you want to reinitialize it:

```bash
python init_database.py --force
```

### Issue: Permission errors

Ensure you have write permissions in the `instance/` directory where the SQLite database is stored.

### Issue: Module import errors

Make sure you're running the scripts from the project root directory and the virtual environment is activated:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Issue: Unicode characters not displaying

The initialization scripts use ASCII characters for Windows compatibility. If you see boxes or strange characters, this is normal and doesn't affect functionality.

## Environment Variables

### SKIP_DB_INIT

Set this to `1` to skip automatic database initialization in `create_app()`:

```bash
export SKIP_DB_INIT=1  # Linux/Mac
set SKIP_DB_INIT=1     # Windows
```

This is useful when you want manual control over initialization, such as in the standalone script.

### FLASK_ENV

Specify the Flask environment:

```bash
export FLASK_ENV=production  # Linux/Mac
set FLASK_ENV=production     # Windows
```

## Security Considerations

1. **Change Default Passwords** - The default passwords (`admin123`, `demo123`, `user123`) should be changed immediately in production

2. **Super Admin Account** - The super admin account has unrestricted access. Secure it properly

3. **Database File** - The SQLite database file is stored in `instance/app.db`. Ensure proper file permissions

4. **Environment-Specific Config** - Use different configurations for development, testing, and production

## Advanced Usage

### Custom Initialization

You can modify [app/utils/init_db.py](app/utils/init_db.py) to customize the initialization:

- Add more default roles
- Create additional companies
- Initialize different plugins
- Add more default users

### Idempotent Design

All initialization functions check if data already exists before creating:

```python
if Role.query.count() > 0:
    print("[OK] Roles already initialized")
    return
```

This makes it safe to run initialization multiple times.

### Database Migrations

For schema changes after initial deployment, use Flask-Migrate:

```bash
# Create a migration
flask db migrate -m "Add new column"

# Apply the migration
flask db upgrade
```

## Related Documentation

- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
