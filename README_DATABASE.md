# Database Configuration Guide

This guide explains how to configure and switch between different databases in the Flask MVC Plugin Application.

## Quick Start

The application is now configured to use **PostgreSQL** by default via the `.env` file.

### Current Configuration

Check your current database connection:

```bash
python check_db.py
```

This will show:
```
[INFO] Using DATABASE_URL from environment
Database URI: postgresql://postgres:abc123@localhost/admin_itmstock
Database Name: admin_itmstock
```

## Supported Databases

- ✅ **SQLite** - File-based, great for development
- ✅ **PostgreSQL** - Recommended for production
- ⚠️ **MySQL** - Supported with additional driver installation

## Configuration Methods

### Method 1: Using .env File (Recommended)

Edit the `.env` file in the project root:

```bash
# PostgreSQL (current default)
DATABASE_URL=postgresql://postgres:abc123@localhost/admin_itmstock

# Or use SQLite for development
# DATABASE_URL=sqlite:///instance/app.db
```

**Benefits:**
- Persists across sessions
- Easy to manage
- Automatically loaded by all scripts
- Can be version-controlled (with .env.example)

### Method 2: Environment Variables

Set the `DATABASE_URL` environment variable:

```bash
# Windows (Command Prompt)
set DATABASE_URL=postgresql://postgres:abc123@localhost/admin_itmstock

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:abc123@localhost/admin_itmstock"

# Linux/Mac
export DATABASE_URL=postgresql://postgres:abc123@localhost/admin_itmstock
```

**Benefits:**
- No file changes needed
- Good for CI/CD pipelines
- Environment-specific

### Method 3: Command-Line Arguments

Use the `--uri` flag with scripts:

```bash
python check_db.py --uri "postgresql://postgres:abc123@localhost/admin_itmstock"
python init_database.py --uri "postgresql://postgres:abc123@localhost/admin_itmstock"
```

**Benefits:**
- One-off queries
- Testing different databases
- No configuration changes

## Switching Between Databases

### SQLite → PostgreSQL

1. **Update .env file:**
   ```bash
   # Comment out SQLite
   # DATABASE_URL=sqlite:///instance/app.db

   # Uncomment PostgreSQL
   DATABASE_URL=postgresql://postgres:abc123@localhost/admin_itmstock
   ```

2. **Install PostgreSQL driver (if not already installed):**
   ```bash
   pip install psycopg2-binary
   ```

3. **Initialize the PostgreSQL database:**
   ```bash
   python init_database.py --force
   ```

### PostgreSQL → SQLite

1. **Update .env file:**
   ```bash
   # Comment out PostgreSQL
   # DATABASE_URL=postgresql://postgres:abc123@localhost/admin_itmstock

   # Uncomment SQLite
   DATABASE_URL=sqlite:///instance/app.db
   ```

2. **Initialize the SQLite database:**
   ```bash
   python init_database.py --force
   ```

## Database Connection Strings

### SQLite

```bash
# Relative path (recommended)
DATABASE_URL=sqlite:///instance/app.db

# Absolute path (Windows)
DATABASE_URL=sqlite:///C:/path/to/database.db

# Absolute path (Linux/Mac)
DATABASE_URL=sqlite:////absolute/path/to/database.db

# In-memory (for testing)
DATABASE_URL=sqlite:///:memory:
```

### PostgreSQL

```bash
# Local database
DATABASE_URL=postgresql://username:password@localhost/dbname

# With custom port
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Remote database
DATABASE_URL=postgresql://username:password@hostname:5432/dbname

# With SSL (production)
DATABASE_URL=postgresql://username:password@hostname:5432/dbname?sslmode=require
```

### MySQL

```bash
# Local database
DATABASE_URL=mysql://username:password@localhost/dbname

# Remote database
DATABASE_URL=mysql://username:password@hostname:3306/dbname
```

**Note:** MySQL requires `mysqlclient` or `PyMySQL`:
```bash
pip install mysqlclient
# or
pip install pymysql
```

## Database Inspection

Check your database contents at any time:

```bash
# Use default from .env
python check_db.py

# Specific environment
python check_db.py --env production

# Custom URI
python check_db.py --uri "postgresql://user:pass@localhost/dbname"
```

## Database Initialization

### First-Time Setup

Initialize the database with default data:

```bash
python init_database.py
```

This creates:
- 4 roles: admin, manager, user, guest
- 2 companies: Demo Company, ACME Corporation
- 1 plugin: stock_plugin
- 3 users: admin, demo_admin, demo_user

### Reset Database

Drop all tables and reinitialize:

```bash
python init_database.py --force
```

**⚠️ WARNING:** This will delete all existing data!

## Production Considerations

### Security Best Practices

1. **Never commit .env file with real credentials**
   - Use `.env.example` as a template
   - Add `.env` to `.gitignore` (already done)

2. **Use strong passwords**
   ```bash
   # Generate a secure password
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Use environment variables in production**
   - Set `DATABASE_URL` via your hosting platform
   - Don't rely on `.env` files in production

4. **Enable SSL for remote databases**
   ```bash
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   ```

### Connection Pooling

For production PostgreSQL, consider connection pooling:

```python
# In app/config/settings.py (ProductionConfig)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### Backup and Restore

**PostgreSQL:**
```bash
# Backup
pg_dump -U postgres admin_itmstock > backup.sql

# Restore
psql -U postgres admin_itmstock < backup.sql
```

**SQLite:**
```bash
# Backup (copy file)
cp instance/app.db instance/app.db.backup

# Restore
cp instance/app.db.backup instance/app.db
```

## Troubleshooting

### Issue: "No module named 'psycopg2'"

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: "Database connection failed"

**Checklist:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check connection string credentials
3. Ensure database exists: `psql -U postgres -c "\l"`
4. Check firewall settings

### Issue: "Permission denied"

**PostgreSQL:**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE admin_itmstock TO postgres;
```

**SQLite:**
- Check file permissions on `instance/app.db`
- Ensure `instance/` directory exists and is writable

### Issue: "Table already exists"

**Solution:**
Use `--force` to drop and recreate:
```bash
python init_database.py --force
```

## Migration Between Databases

To migrate data from SQLite to PostgreSQL:

1. **Export data from SQLite:**
   ```bash
   # Using the app
   python -c "from app import create_app, db; from app.models import *; ..."
   ```

2. **Update .env to PostgreSQL**

3. **Initialize PostgreSQL:**
   ```bash
   python init_database.py --force
   ```

4. **Import data** (custom script or manual)

## Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_URL` | Database connection string | SQLite | `postgresql://user:pass@localhost/db` |
| `FLASK_ENV` | Flask environment | `development` | `production`, `testing` |
| `SECRET_KEY` | Session secret key | Auto-generated | Long random string |
| `PORT` | Server port | `5000` | `8000` |
| `DEBUG` | Debug mode | `True` | `False` for production |

## Testing

Run tests with different databases:

```bash
# SQLite (default for tests)
pytest

# PostgreSQL
DATABASE_URL=postgresql://postgres:abc123@localhost/test_db pytest

# In-memory (fastest)
DATABASE_URL=sqlite:///:memory: pytest
```

## Further Reading

- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Database Initialization Guide](DATABASE_INITIALIZATION.md)

## Support

For database-related issues:
1. Check this guide first
2. Review error messages carefully
3. Check the database logs
4. Verify connection strings and credentials
