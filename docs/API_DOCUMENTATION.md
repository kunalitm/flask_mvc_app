# API Documentation

Complete API reference for the Flask MVC Plugin Application.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Response Format

All responses are in JSON format.

Success responses:
```json
{
  "data": {...},
  "message": "Success message"
}
```

Error responses:
```json
{
  "error": "Error type",
  "message": "Error description"
}
```

---

## User Management API

### POST /users/login
Authenticate a user and receive a JWT token.

**Request:**
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "roles": [
      {
        "id": 1,
        "name": "admin"
      }
    ]
  }
}
```

### GET /users/
Get all users (paginated).

**Request:**
```bash
curl -X GET http://localhost:5000/api/users/?page=1&per_page=20 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "System",
      "last_name": "Administrator",
      "is_active": true,
      "roles": [...]
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### GET /users/me
Get current authenticated user.

**Request:**
```bash
curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "roles": [...]
}
```

### GET /users/:id
Get user by ID.

**Request:**
```bash
curl -X GET http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "System",
  "last_name": "Administrator",
  "is_active": true,
  "roles": [...]
}
```

### POST /users/
Create a new user (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role_ids": [2]
  }'
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 2,
    "username": "newuser",
    "email": "user@example.com",
    "roles": [...]
  }
}
```

### PUT /users/:id
Update user information.

**Request:**
```bash
curl -X PUT http://localhost:5000/api/users/2 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "first_name": "Jane"
  }'
```

**Response:**
```json
{
  "message": "User updated successfully",
  "user": {...}
}
```

### DELETE /users/:id
Delete a user (admin only).

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/users/2 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

### POST /users/:id/roles
Assign role to user (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/users/2/roles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 2
  }'
```

**Response:**
```json
{
  "message": "Role assigned successfully",
  "user": {...}
}
```

### DELETE /users/:id/roles/:roleId
Remove role from user (admin only).

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/users/2/roles/2 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Role removed successfully",
  "user": {...}
}
```

---

## Role Management API

### GET /roles/
Get all roles.

**Request:**
```bash
curl -X GET http://localhost:5000/api/roles/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "Administrator with full system access",
      "permissions": ["users.*", "roles.*", "plugins.*", "*"],
      "is_system": true,
      "user_count": 1
    }
  ]
}
```

### GET /roles/:id
Get role by ID.

**Request:**
```bash
curl -X GET http://localhost:5000/api/roles/1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": 1,
  "name": "admin",
  "description": "Administrator with full system access",
  "permissions": ["users.*", "roles.*", "*"],
  "is_system": true,
  "user_count": 1
}
```

### POST /roles/
Create a new role (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/roles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "moderator",
    "description": "Moderator role",
    "permissions": ["users.read", "users.update"]
  }'
```

**Response:**
```json
{
  "message": "Role created successfully",
  "role": {
    "id": 4,
    "name": "moderator",
    "permissions": ["users.read", "users.update"]
  }
}
```

### PUT /roles/:id
Update role information (admin only).

**Request:**
```bash
curl -X PUT http://localhost:5000/api/roles/4 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "permissions": ["users.read", "users.update", "users.delete"]
  }'
```

**Response:**
```json
{
  "message": "Role updated successfully",
  "role": {...}
}
```

### DELETE /roles/:id
Delete a role (admin only, cannot delete system roles).

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/roles/4 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Role deleted successfully"
}
```

### GET /roles/:id/permissions
Get permissions for a role.

**Request:**
```bash
curl -X GET http://localhost:5000/api/roles/1/permissions \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "role": "admin",
  "permissions": ["users.*", "roles.*", "plugins.*", "*"]
}
```

### PUT /roles/:id/permissions
Update permissions for a role (admin only).

**Request:**
```bash
curl -X PUT http://localhost:5000/api/roles/4/permissions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": ["users.read", "users.update"]
  }'
```

**Response:**
```json
{
  "message": "Permissions updated successfully",
  "role": {...}
}
```

---

## Plugin Management API

### GET /plugins/
Get all plugins.

**Request:**
```bash
curl -X GET http://localhost:5000/api/plugins/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "plugins": [
    {
      "id": 1,
      "name": "stock_plugin",
      "version": "1.0.0",
      "description": "Stock/Inventory management plugin",
      "author": "MVC Plugin System",
      "is_enabled": true,
      "is_system": false,
      "config": {}
    }
  ]
}
```

### GET /plugins/:id
Get plugin by ID.

**Request:**
```bash
curl -X GET http://localhost:5000/api/plugins/1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": 1,
  "name": "stock_plugin",
  "version": "1.0.0",
  "description": "Stock/Inventory management plugin",
  "is_enabled": true,
  "config": {}
}
```

### POST /plugins/:id/enable
Enable a plugin (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/plugins/1/enable \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Plugin enabled successfully",
  "plugin": {...}
}
```

### POST /plugins/:id/disable
Disable a plugin (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/plugins/1/disable \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Plugin disabled successfully",
  "plugin": {...}
}
```

### GET /plugins/:id/config
Get plugin configuration.

**Request:**
```bash
curl -X GET http://localhost:5000/api/plugins/1/config \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "plugin": "stock_plugin",
  "config": {
    "api_key": "xxx",
    "max_items": 100
  }
}
```

### PUT /plugins/:id/config
Update plugin configuration (admin only).

**Request:**
```bash
curl -X PUT http://localhost:5000/api/plugins/1/config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "api_key": "new_key",
      "max_items": 200
    }
  }'
```

**Response:**
```json
{
  "message": "Plugin configuration updated successfully",
  "plugin": {...}
}
```

### POST /plugins/:id/reload
Reload a plugin (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/plugins/1/reload \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Plugin reloaded successfully",
  "plugin": {...}
}
```

### POST /plugins/discover
Discover new plugins (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/plugins/discover \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Plugin discovery completed",
  "discovered": 1,
  "plugins": [...]
}
```

### GET /plugins/enabled
Get all enabled plugins.

**Request:**
```bash
curl -X GET http://localhost:5000/api/plugins/enabled \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "plugins": [...]
}
```

---

## Stock Plugin API

These endpoints are provided by the stock_plugin demo plugin (when enabled).

### GET /stock/items
Get all stock items.

**Request:**
```bash
curl -X GET http://localhost:5000/api/stock/items \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "items": [
    {
      "id": "item1",
      "name": "Product A",
      "quantity": 100,
      "price": 29.99,
      "description": "Product description"
    }
  ]
}
```

### GET /stock/items/:id
Get stock item by ID.

**Request:**
```bash
curl -X GET http://localhost:5000/api/stock/items/item1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "item1",
  "name": "Product A",
  "quantity": 100,
  "price": 29.99
}
```

### POST /stock/items
Create a new stock item (admin only).

**Request:**
```bash
curl -X POST http://localhost:5000/api/stock/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "item1",
    "name": "Product A",
    "quantity": 100,
    "price": 29.99,
    "description": "Product description"
  }'
```

**Response:**
```json
{
  "message": "Stock item created successfully",
  "item": {...}
}
```

### PUT /stock/items/:id
Update a stock item (admin only).

**Request:**
```bash
curl -X PUT http://localhost:5000/api/stock/items/item1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product A",
    "quantity": 150,
    "price": 34.99
  }'
```

**Response:**
```json
{
  "message": "Stock item updated successfully",
  "item": {...}
}
```

### DELETE /stock/items/:id
Delete a stock item (admin only).

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/stock/items/item1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Stock item deleted successfully"
}
```

### GET /stock/stats
Get stock statistics.

**Request:**
```bash
curl -X GET http://localhost:5000/api/stock/stats \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "total_items": 10,
  "total_quantity": 500,
  "total_value": 5000.00,
  "low_stock_items": 2
}
```

---

## Error Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider adding rate limiting to prevent abuse.

## Versioning

The API is currently at version 1. Future versions may be accessed via `/api/v2/` prefix.
