# Quick Start Guide

Get up and running with the Flask MVC Plugin Application in minutes.

## Installation (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run.py
```

The application will automatically:
- Create the SQLite database
- Set up default roles (admin, user, guest)
- Create an admin user (username: `admin`, password: `admin123`)
- Load and initialize plugins

## First Steps

### 1. Login
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Save the token from the response.

### 2. View Your Profile
```bash
export TOKEN="your-token-here"

curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. List All Plugins
```bash
curl -X GET http://localhost:5000/api/plugins/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Enable the Stock Plugin
```bash
curl -X POST http://localhost:5000/api/plugins/1/enable \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Use the Stock Plugin
```bash
# Create a stock item
curl -X POST http://localhost:5000/api/stock/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "laptop001",
    "name": "Dell Laptop",
    "quantity": 50,
    "price": 899.99,
    "description": "Dell XPS 15 Laptop"
  }'

# Get all stock items
curl -X GET http://localhost:5000/api/stock/items \
  -H "Authorization: Bearer $TOKEN"

# Get stock statistics
curl -X GET http://localhost:5000/api/stock/stats \
  -H "Authorization: Bearer $TOKEN"
```

## Common Tasks

### Create a New User
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
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

### Create a Custom Role
```bash
curl -X POST http://localhost:5000/api/roles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "moderator",
    "description": "Moderator with limited admin access",
    "permissions": ["users.read", "users.update", "plugins.read"]
  }'
```

### Assign Role to User
```bash
curl -X POST http://localhost:5000/api/users/2/roles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 4}'
```

## What's Next?

1. **Read the API Documentation**: [docs/API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Create Your Own Plugin**: [docs/PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)
3. **Deploy as Microservices**: [docs/MICROSERVICES.md](MICROSERVICES.md)
4. **Change Admin Password**: Use the update user endpoint
5. **Configure Environment**: Copy `.env.example` to `.env` and customize

## Troubleshooting

**Port already in use?**
```bash
export PORT=8000
python run.py
```

**Need to reset database?**
```bash
rm instance/app.db
python run.py
```

**Plugin not loading?**
```bash
curl -X POST http://localhost:5000/api/plugins/discover \
  -H "Authorization: Bearer $TOKEN"
```

## Project Structure Overview

```
flask_mvc_app/
├── app/                    # Application package
│   ├── models/            # Database models (MVC: Model)
│   ├── views/             # View layer (MVC: View)
│   ├── controllers/       # Business logic (MVC: Controller)
│   ├── plugins/           # Plugin system
│   │   ├── base/         # Base plugin classes
│   │   ├── manager/      # Plugin manager
│   │   └── stock_plugin/ # Demo plugin
│   ├── config/           # Configuration
│   └── utils/            # Utilities (RBAC, etc.)
├── docs/                  # Documentation
├── instance/              # Instance data (database, configs)
└── run.py                # Application entry point
```

## Key Features to Explore

1. **RBAC** - Role-based access control with decorators
2. **Plugin System** - Dynamic plugin loading and management
3. **RESTful API** - Complete CRUD operations
4. **JWT Auth** - Stateless authentication
5. **MVC Architecture** - Clean code organization

## Default Credentials

**Admin User**
- Username: `admin`
- Password: `admin123`
- Role: `admin` (full access)

**IMPORTANT**: Change the admin password in production!

```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "new-secure-password"}'
```

## Support

- Full Documentation: [README.md](../README.md)
- API Reference: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Plugin Guide: [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)
