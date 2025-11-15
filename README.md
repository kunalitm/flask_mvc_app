# Flask MVC Application with Plugin Architecture

A comprehensive web application built with Flask following MVC (Model-View-Controller) architecture and featuring a dynamic plugin system for extensibility.

## Features

### Core Features
- **MVC Architecture**: Clean separation of concerns with Models, Views, and Controllers
- **Plugin System**: Dynamic plugin loading and management with lifecycle hooks
- **User Management**: Complete user CRUD operations with authentication
- **Role Management**: Flexible role-based access control (RBAC)
- **RESTful API**: Well-documented API endpoints for all operations
- **JWT Authentication**: Secure token-based authentication
- **Database Migrations**: Flask-Migrate for database version control

### Plugin Architecture
- **Dynamic Loading**: Plugins are discovered and loaded at runtime
- **Lifecycle Management**: Enable/disable plugins without server restart
- **Plugin Configuration**: Per-plugin configuration storage
- **Isolated Execution**: Plugins run in isolated contexts
- **Hot Reloading**: Reload plugins without restarting the application

### Security
- **RBAC**: Role-based access control with granular permissions
- **Password Hashing**: Secure password storage using bcrypt
- **JWT Tokens**: Stateless authentication with token expiration
- **Permission Decorators**: Easy-to-use decorators for protecting routes

## Project Structure

```
flask_mvc_app/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration classes
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── role.py              # Role model
│   │   ├── user_role.py         # User-Role association
│   │   └── plugin.py            # Plugin model
│   ├── views/                   # View layer (templates/serializers)
│   │   └── __init__.py
│   ├── controllers/             # Controller layer (business logic)
│   │   ├── __init__.py
│   │   ├── user_controller.py   # User API endpoints
│   │   ├── role_controller.py   # Role API endpoints
│   │   └── plugin_controller.py # Plugin API endpoints
│   ├── plugins/                 # Plugin system
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── base_plugin.py   # Base plugin class
│   │   ├── manager/
│   │   │   ├── __init__.py
│   │   │   └── plugin_manager.py # Plugin lifecycle manager
│   │   └── stock_plugin/        # Demo plugin
│   │       ├── __init__.py
│   │       └── plugin.py
│   ├── services/                # Business logic services
│   │   └── __init__.py
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── rbac.py              # RBAC decorators
│       └── init_db.py           # Database initialization
├── docs/
│   └── API_DOCUMENTATION.md     # Complete API reference
├── instance/                    # Instance-specific files (gitignored)
│   ├── app.db                   # SQLite database
│   └── plugin_configs/          # Plugin configurations
├── tests/                       # Test suite
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables example
├── .gitignore
└── README.md
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd flask_mvc_app
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and update the values as needed
```

5. **Initialize the database**
```bash
# The database will be automatically created on first run
python run.py
```

The application will:
- Create the database schema
- Initialize default roles (admin, user, guest)
- Create a default admin user (username: admin, password: admin123)
- Discover and load available plugins

## Running the Application

### Development Mode
```bash
python run.py
```

The server will start on `http://localhost:5000`

### Production Mode
```bash
export FLASK_ENV=production
export SECRET_KEY="your-production-secret-key"
python run.py
```

### Using Environment Variables
```bash
export FLASK_ENV=development
export PORT=8000
export DATABASE_URL=postgresql://user:pass@localhost/dbname
python run.py
```

## Quick Start Guide

### 1. Login and Get Token
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Save the token from the response.

### 2. Get Current User
```bash
curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer <your-token>"
```

### 3. Create a New User
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role_ids": [2]
  }'
```

### 4. Enable a Plugin
```bash
curl -X POST http://localhost:5000/api/plugins/1/enable \
  -H "Authorization: Bearer <your-token>"
```

### 5. Use Plugin Features (Stock Plugin Example)
```bash
# Create a stock item
curl -X POST http://localhost:5000/api/stock/items \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "item1",
    "name": "Product A",
    "quantity": 100,
    "price": 29.99
  }'

# Get stock statistics
curl -X GET http://localhost:5000/api/stock/stats \
  -H "Authorization: Bearer <your-token>"
```

## Creating a Custom Plugin

### 1. Create Plugin Directory
```bash
mkdir -p app/plugins/my_plugin
```

### 2. Create Plugin Class
Create `app/plugins/my_plugin/plugin.py`:

```python
from app.plugins.base.base_plugin import BasePlugin
from flask import Blueprint, jsonify

class MyPlugin(BasePlugin):
    @property
    def name(self):
        return "my_plugin"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "My custom plugin"

    def on_enable(self):
        """Called when plugin is enabled"""
        self.logger.info("My plugin enabled!")
        if self.app:
            self.register_blueprints(self.app)

    def on_disable(self):
        """Called when plugin is disabled"""
        self.logger.info("My plugin disabled!")

    def register_blueprints(self, app):
        """Register plugin routes"""
        bp = Blueprint('my_plugin', __name__)

        @bp.route('/hello', methods=['GET'])
        def hello():
            return jsonify({"message": "Hello from my plugin!"})

        app.register_blueprint(bp, url_prefix='/api/my_plugin')
```

### 3. Discover and Enable Plugin
```bash
# Discover new plugins
curl -X POST http://localhost:5000/api/plugins/discover \
  -H "Authorization: Bearer <your-token>"

# Enable your plugin
curl -X POST http://localhost:5000/api/plugins/<id>/enable \
  -H "Authorization: Bearer <your-token>"
```

## API Documentation

Complete API documentation with examples is available in [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

### API Endpoints Overview

**User Management**
- `POST /api/users/login` - User authentication
- `GET /api/users/` - List all users
- `GET /api/users/me` - Get current user
- `POST /api/users/` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user
- `POST /api/users/:id/roles` - Assign role
- `DELETE /api/users/:id/roles/:roleId` - Remove role

**Role Management**
- `GET /api/roles/` - List all roles
- `GET /api/roles/:id` - Get role details
- `POST /api/roles/` - Create role
- `PUT /api/roles/:id` - Update role
- `DELETE /api/roles/:id` - Delete role
- `GET /api/roles/:id/permissions` - Get permissions
- `PUT /api/roles/:id/permissions` - Update permissions

**Plugin Management**
- `GET /api/plugins/` - List all plugins
- `GET /api/plugins/:id` - Get plugin details
- `POST /api/plugins/:id/enable` - Enable plugin
- `POST /api/plugins/:id/disable` - Disable plugin
- `GET /api/plugins/:id/config` - Get configuration
- `PUT /api/plugins/:id/config` - Update configuration
- `POST /api/plugins/:id/reload` - Reload plugin
- `POST /api/plugins/discover` - Discover new plugins

**Stock Plugin** (when enabled)
- `GET /api/stock/items` - List stock items
- `POST /api/stock/items` - Create stock item
- `GET /api/stock/items/:id` - Get stock item
- `PUT /api/stock/items/:id` - Update stock item
- `DELETE /api/stock/items/:id` - Delete stock item
- `GET /api/stock/stats` - Get statistics

## Running as Microservices

The application can be split into separate services:

### User Service
```python
# user_service.py
from app import create_app
from app.config.settings import config

app = create_app(config['production'])

# Only register user blueprint
from app.controllers.user_controller import user_bp
app.register_blueprint(user_bp, url_prefix='/api/users')

if __name__ == '__main__':
    app.run(port=5001)
```

### Plugin Service
```python
# plugin_service.py
from app import create_app
from app.config.settings import config

app = create_app(config['production'])

# Only register plugin blueprint
from app.controllers.plugin_controller import plugin_bp
app.register_blueprint(plugin_bp, url_prefix='/api/plugins')

if __name__ == '__main__':
    app.run(port=5002)
```

## Security Best Practices

1. **Change Default Credentials**: Update the admin password immediately
2. **Use Strong Secret Key**: Generate a secure random key for production
3. **Environment Variables**: Never commit `.env` file to version control
4. **HTTPS Only**: Use HTTPS in production
5. **Database Security**: Use PostgreSQL/MySQL with proper authentication
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Input Validation**: Always validate and sanitize user input

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Database Migrations

Create a migration:
```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

Rollback a migration:
```bash
flask db downgrade
```

## Default Roles and Permissions

**Admin Role**
- Permissions: `["users.*", "roles.*", "plugins.*", "*"]`
- Full system access

**User Role**
- Permissions: `["users.read", "users.update_self"]`
- Basic user access

**Guest Role**
- Permissions: `["users.read"]`
- Read-only access

## Troubleshooting

### Database Issues
```bash
# Delete database and recreate
rm instance/app.db
python run.py
```

### Plugin Not Loading
- Check plugin directory structure
- Verify `plugin.py` exists
- Check logs for errors
- Use `/api/plugins/discover` endpoint

### Authentication Issues
- Verify token in Authorization header
- Check token expiration (24 hours)
- Ensure user is active

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/your-repo/issues)
- Documentation: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

## Changelog

### Version 1.0.0
- Initial release
- MVC architecture implementation
- Plugin system with dynamic loading
- User and role management
- JWT authentication
- Stock plugin demo
- Complete API documentation
