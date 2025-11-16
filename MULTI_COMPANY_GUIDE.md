# Multi-Company (Multi-Tenant) Management Guide

## Overview

The Flask MVC application now supports multi-company management with the following features:

### Key Features
- **Super Admin**: Can manage all companies, users, roles, and plugins
- **Company Isolation**: Each company has its own users and plugin installations
- **Plugin Management**: Super admin can install/enable plugins for specific companies
- **Granular Permissions**: CRUD permissions for users, roles, companies, and plugins

## Architecture

### New Models

#### 1. Company Model (`app/models/company.py`)
```python
- id
- name (unique)
- slug (URL-friendly identifier)
- description
- email, phone, address
- is_active
- max_users (user limit)
- settings (JSON)
- created_at, updated_at
```

#### 2. CompanyPlugin Model (`app/models/company_plugin.py`)
Association table connecting companies to plugins with:
```python
- company_id (FK)
- plugin_id (FK)
- is_enabled (company-specific)
- config (company-specific plugin config)
- installed_at, enabled_at, disabled_at
```

#### 3. Updated User Model
New fields:
```python
- is_super_admin (boolean)
- company_id (FK, NULL for super admin)
```

### Permission System

#### Granular CRUD Permissions

Permissions are defined in JSON format for each role:

```json
{
  "permissions": [
    "users.create",
    "users.read",
    "users.update",
    "users.delete",
    "roles.create",
    "roles.read",
    "roles.update",
    "roles.delete",
    "companies.create",
    "companies.read",
    "companies.update",
    "companies.delete",
    "plugins.create",
    "plugins.read",
    "plugins.update",
    "plugins.delete"
  ]
}
```

#### Wildcard Permissions

- `"users.*"` - All user permissions
- `"*"` - All permissions (super admin)

#### Super Admin

Super admin users:
- Have `is_super_admin = True`
- Have `company_id = NULL`
- Bypass all permission checks
- Can manage all companies

## API Endpoints

### Company Management

```
GET    /api/companies/                  - List all companies
GET    /api/companies/<id>              - Get company details
POST   /api/companies/                  - Create company (super admin)
PUT    /api/companies/<id>              - Update company
DELETE /api/companies/<id>              - Delete company (super admin)
GET    /api/companies/<id>/stats        - Get company statistics
GET    /api/companies/<id>/users        - Get company users
```

### Company-Plugin Management

```
GET    /api/companies/<id>/plugins                        - List plugins for company
POST   /api/companies/<id>/plugins/<plugin_id>/install    - Install plugin to company
POST   /api/companies/<id>/plugins/<plugin_id>/enable     - Enable plugin for company
POST   /api/companies/<id>/plugins/<plugin_id>/disable    - Disable plugin for company
GET    /api/companies/<id>/plugins/<plugin_id>/config     - Get plugin config
PUT    /api/companies/<id>/plugins/<plugin_id>/config     - Update plugin config
```

## Database Schema Changes

### New Tables

1. **companies**
   - Primary table for company/tenant information

2. **company_plugins**
   - Junction table for company-plugin associations
   - Stores company-specific plugin configuration

### Modified Tables

1. **users**
   - Added `is_super_admin` column
   - Added `company_id` foreign key (nullable)

## Setup Instructions

### 1. Initialize Super Admin

Run the initialization script to create the first super admin:

```bash
python init_super_admin.py
```

This creates:
- Super admin user (username: superadmin, password: superadmin123)
- Super admin role with all permissions

### 2. Create Companies

As super admin, create companies via API:

```bash
curl -X POST http://localhost:5000/api/companies/ \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "description": "First company",
    "email": "contact@acme.com",
    "max_users": 50
  }'
```

### 3. Create Company Users

Create users for a specific company:

```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_acme",
    "email": "john@acme.com",
    "password": "password123",
    "company_id": 1,
    "role_ids": [2]
  }'
```

### 4. Install Plugins to Company

```bash
curl -X POST http://localhost:5000/api/companies/1/plugins/1/install \
  -H "Authorization: Bearer <super_admin_token>"
```

### 5. Enable Plugin for Company

```bash
curl -X POST http://localhost:5000/api/companies/1/plugins/1/enable \
  -H "Authorization: Bearer <super_admin_token>"
```

## Permission Examples

### Super Admin Role
```json
{
  "name": "super_admin",
  "permissions": ["*"]
}
```

### Company Admin Role
```json
{
  "name": "company_admin",
  "permissions": [
    "users.*",
    "roles.read",
    "plugins.read"
  ]
}
```

### Company User Role
```json
{
  "name": "company_user",
  "permissions": [
    "users.read",
    "users.update",
    "roles.read"
  ]
}
```

### Company Manager Role
```json
{
  "name": "company_manager",
  "permissions": [
    "users.create",
    "users.read",
    "users.update",
    "users.delete",
    "roles.read",
    "roles.create",
    "roles.update"
  ]
}
```

## Access Control

### Super Admin
- Can access ALL companies
- Can create/update/delete companies
- Can assign plugins to companies
- Can create users in any company

### Company Admin
- Can only access their own company
- Can manage users within their company
- Can view available plugins
- Cannot install plugins (only super admin)

### Company User
- Can only access their own company
- Limited permissions based on role
- Cannot manage other users

## Frontend Integration

### Company Management Page
- List all companies (super admin)
- Create/edit/delete companies
- View company statistics
- Manage company settings

### Plugin Assignment
- View all available plugins
- Install plugins to companies (super admin)
- Enable/disable plugins per company
- Configure plugin settings per company

### User Management Updates
- Filter users by company
- Assign company when creating users
- Show company in user list

## Security Considerations

1. **Strict Isolation**: Users can only access data from their own company
2. **Super Admin Protection**: Super admin accounts should be carefully controlled
3. **Permission Validation**: All endpoints check both authentication and permissions
4. **Company Validation**: API endpoints verify company_id matches authenticated user

## Migration Path

### For Existing Installations

1. Backup database
2. Run migration to add new tables and columns
3. Create default company for existing users
4. Run super admin initialization
5. Assign existing users to companies

## Testing

### Test Scenarios

1. **Super Admin Can**:
   - Create companies
   - View all companies
   - Create users in any company
   - Install plugins to companies

2. **Company Admin Can**:
   - View only their company
   - Manage users in their company
   - Cannot access other companies

3. **Company User Can**:
   - Access resources based on permissions
   - Cannot see other companies' data

## Troubleshooting

### User Cannot Access Company Resources
- Check `company_id` in user record
- Verify company is active (`is_active = true`)
- Check user has appropriate role with permissions

### Plugin Not Available for Company
- Check if plugin is installed for company in `company_plugins`
- Verify plugin is enabled (`is_enabled = true`)
- Check company-specific plugin configuration

### Permission Denied Errors
- Verify user's role has required permission
- Check permission string format (e.g., "users.create")
- Ensure role permissions are properly formatted JSON

## Example Workflows

### Create New Company Workflow

1. Super admin logs in
2. Creates new company via API
3. Creates company admin user
4. Assigns company admin role
5. Installs required plugins for company
6. Enables plugins
7. Company admin can now log in and manage their company

### Plugin Rollout Workflow

1. Super admin views available plugins
2. Selects companies to receive plugin
3. Installs plugin to selected companies
4. Configures plugin per company
5. Enables plugin when ready
6. Company users can access plugin features

## Future Enhancements

- Company-specific branding/themes
- Company billing and subscription management
- Inter-company data sharing (controlled)
- Company-level analytics and reporting
- Multi-company search and aggregation
