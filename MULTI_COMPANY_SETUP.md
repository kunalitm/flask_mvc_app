# Multi-Company Setup Guide

## 🚀 Quick Start

### Step 1: Initialize Multi-Company Database

Run the initialization script to set up the multi-company schema:

```bash
python init_multi_company.py
```

This will:
- ✅ Create `companies` table
- ✅ Create `company_plugins` table
- ✅ Add `is_super_admin` and `company_id` columns to `users` table
- ✅ Create default company for existing users
- ✅ Create super admin role with all permissions
- ✅ Create super admin user
- ✅ Update admin role permissions
- ✅ Create company admin role

### Step 2: Login as Super Admin

**Credentials:**
- Username: `superadmin`
- Password: `superadmin123`

```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "superadmin", "password": "superadmin123"}'
```

Save the returned token for subsequent requests.

### Step 3: Create Your First Company

```bash
curl -X POST http://localhost:5000/api/companies/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "description": "Technology company",
    "email": "contact@acme.com",
    "phone": "+1-555-0100",
    "max_users": 50
  }'
```

### Step 4: Create Company Admin User

```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acme_admin",
    "email": "admin@acme.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "company_id": 2,
    "role_ids": [4]
  }'
```

### Step 5: Install Plugin to Company

```bash
# Install stock plugin to company ID 2
curl -X POST http://localhost:5000/api/companies/2/plugins/1/install \
  -H "Authorization: Bearer YOUR_TOKEN"

# Enable the plugin
curl -X POST http://localhost:5000/api/companies/2/plugins/1/enable \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📋 Permission Structure

### Permission Format

Permissions use dot notation:
- `resource.action`
- Examples: `users.create`, `companies.read`, `plugins.update`

### CRUD Permissions

Each resource has 4 basic permissions:
- `.create` - Create new resources
- `.read` - View resources
- `.update` - Modify resources
- `.delete` - Remove resources

### Available Permissions

```
users.create
users.read
users.update
users.delete

roles.create
roles.read
roles.update
roles.delete

companies.create
companies.read
companies.update
companies.delete

plugins.create
plugins.read
plugins.update
plugins.delete
```

### Wildcard Permissions

- `users.*` - All user permissions
- `roles.*` - All role permissions
- `companies.*` - All company permissions
- `plugins.*` - All plugin permissions
- `*` - All permissions (super admin only)

## 👥 User Types

### 1. Super Admin
- **Field:** `is_super_admin = true`, `company_id = NULL`
- **Permissions:** `["*"]`
- **Can Access:** All companies and resources
- **Cannot:** Be restricted by company boundaries

### 2. Company Admin
- **Field:** `is_super_admin = false`, `company_id = X`
- **Permissions:** `["users.*", "roles.read", "companies.read"]`
- **Can Access:** Only their company's resources
- **Cannot:** Create companies or assign plugins

### 3. Company User
- **Field:** `is_super_admin = false`, `company_id = X`
- **Permissions:** Based on assigned roles
- **Can Access:** Limited by role permissions
- **Cannot:** Manage users or companies

## 🏢 Company Management

### Create Company

```json
POST /api/companies/
{
  "name": "Company Name",
  "description": "Company description",
  "email": "contact@company.com",
  "phone": "+1-555-0100",
  "address": "123 Main St, City, State 12345",
  "max_users": 50,
  "settings": {
    "theme": "light",
    "timezone": "UTC"
  }
}
```

### List Companies

```bash
GET /api/companies/
Query Parameters:
  - page: Page number (default: 1)
  - per_page: Items per page (default: 10)
  - include_stats: Include statistics (default: false)
```

### Update Company

```json
PUT /api/companies/<id>
{
  "name": "Updated Name",
  "max_users": 100,
  "is_active": true
}
```

### Delete Company

```bash
DELETE /api/companies/<id>
Note: Company must have no users before deletion
```

### Get Company Statistics

```bash
GET /api/companies/<id>/stats
Returns:
{
  "user_count": 15,
  "max_users": 50,
  "plugin_count": 3,
  "enabled_plugins": 2
}
```

## 🔌 Plugin Management

### Install Plugin to Company

```bash
POST /api/companies/<company_id>/plugins/<plugin_id>/install
{
  "config": {
    "setting1": "value1",
    "setting2": "value2"
  }
}
```

### Enable Plugin for Company

```bash
POST /api/companies/<company_id>/plugins/<plugin_id>/enable
```

### Disable Plugin for Company

```bash
POST /api/companies/<company_id>/plugins/<plugin_id>/disable
```

### Get Company Plugins

```bash
GET /api/companies/<company_id>/plugins
Returns list of all plugins with company-specific status
```

### Update Plugin Configuration

```json
PUT /api/companies/<company_id>/plugins/<plugin_id>/config
{
  "config": {
    "updated_setting": "new_value"
  }
}
```

## 🔒 Security & Access Control

### Super Admin Access
- Sees all companies in GET /api/companies/
- Can create/update/delete any company
- Can install plugins to any company
- Can create users in any company

### Company User Access
- Sees only their own company in GET /api/companies/
- Cannot create or delete companies
- Cannot install plugins (super admin only)
- Can only manage users in their company (if permissions allow)

### Permission Checking
Every API endpoint checks:
1. **Authentication**: Valid JWT token
2. **Authorization**: Required permission in user's roles
3. **Company Scope**: User can only access their company (unless super admin)

## 📊 Example Role Configurations

### Super Admin Role
```json
{
  "name": "super_admin",
  "description": "Super administrator with full access",
  "permissions": ["*"],
  "is_system": true
}
```

### Company Admin Role
```json
{
  "name": "company_admin",
  "description": "Company administrator",
  "permissions": [
    "users.create",
    "users.read",
    "users.update",
    "users.delete",
    "roles.read",
    "companies.read"
  ],
  "is_system": false
}
```

### Company Manager Role
```json
{
  "name": "company_manager",
  "description": "Can manage users and view roles",
  "permissions": [
    "users.*",
    "roles.read"
  ],
  "is_system": false
}
```

### Company User Role
```json
{
  "name": "company_user",
  "description": "Basic company user",
  "permissions": [
    "users.read",
    "roles.read"
  ],
  "is_system": false
}
```

## 🧪 Testing the Setup

### 1. Test Super Admin Login
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "superadmin", "password": "superadmin123"}'
```

### 2. Test Create Company
```bash
curl -X POST http://localhost:5000/api/companies/ \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Company", "max_users": 10}'
```

### 3. Test Create Company User
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@company.com",
    "password": "test123",
    "company_id": 2
  }'
```

### 4. Test Company User Login
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'
```

### 5. Test Company Isolation
```bash
# Company user tries to access another company (should fail)
curl -X GET http://localhost:5000/api/companies/1 \
  -H "Authorization: Bearer COMPANY_USER_TOKEN"
```

## 🚨 Troubleshooting

### "Permission denied" errors
- Check user's roles have required permissions
- Verify permission string format
- Ensure user is active

### "Access denied" errors
- User trying to access different company
- Only super admin can access all companies

### Plugin not available
- Check if plugin is installed for company
- Verify plugin is enabled
- Check company-specific plugin config

### Cannot create users
- Check company's `max_users` limit
- Verify user has `users.create` permission

## 📝 Database Schema

### Companies Table
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    max_users INTEGER DEFAULT 10,
    settings TEXT,  -- JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Company_Plugins Table
```sql
CREATE TABLE company_plugins (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    plugin_id INTEGER NOT NULL,
    is_enabled BOOLEAN DEFAULT 0,
    config TEXT,  -- JSON
    installed_at TIMESTAMP,
    enabled_at TIMESTAMP,
    disabled_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (plugin_id) REFERENCES plugins(id),
    UNIQUE (company_id, plugin_id)
)
```

### Updated Users Table
```sql
ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN company_id INTEGER REFERENCES companies(id);
```

## 🎯 Next Steps

1. **Frontend Integration**
   - Create Company management UI
   - Add company selector for super admin
   - Update user creation form with company selection
   - Add plugin assignment interface

2. **Additional Features**
   - Company-specific branding
   - Usage analytics per company
   - Billing integration
   - Company-level settings

3. **Security Enhancements**
   - Rate limiting per company
   - Audit logging
   - IP whitelisting per company
   - Two-factor authentication

## 📚 Additional Documentation

- [MULTI_COMPANY_GUIDE.md](MULTI_COMPANY_GUIDE.md) - Detailed architecture guide
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - Complete API reference
- [README.md](README.md) - General setup and usage

## ⚠️ Important Notes

1. **Super Admin Security**: Protect super admin credentials carefully
2. **Company Isolation**: All data is strictly isolated by company_id
3. **Plugin Assignment**: Only super admin can install/enable plugins for companies
4. **User Limit**: Respect the `max_users` setting for each company
5. **Backup**: Always backup database before running initialization scripts
