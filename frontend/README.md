# Flask MVC Frontend

A modern React-based frontend for the Flask MVC application with plugin architecture.

## Features

- **Authentication**: Secure login with JWT token-based authentication
- **User Management**: Full CRUD operations for users with role assignment
- **Role Management**: Create and manage roles with custom permissions
- **Plugin Management**: Enable/disable plugins, configure settings, and discover new plugins
- **Stock Inventory**: Manage inventory items with real-time statistics (demo plugin)
- **Responsive Design**: Built with Tailwind CSS for a modern, mobile-friendly interface

## Tech Stack

- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Tailwind CSS** - Utility-first CSS framework

## Prerequisites

- Node.js 16+ and npm/yarn
- Flask backend running on `http://localhost:5000`

## Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## Development

1. **Start the development server**:
   ```bash
   npm run dev
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:3000`

3. **Login with default credentials**:
   - Username: `admin`
   - Password: `admin123`

## Build for Production

1. **Create production build**:
   ```bash
   npm run build
   ```

2. **Preview production build**:
   ```bash
   npm run preview
   ```

The build output will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   └── Login.jsx              # Login page
│   │   ├── Dashboard/
│   │   │   └── Dashboard.jsx          # Main dashboard
│   │   ├── Layout/
│   │   │   └── Layout.jsx             # Main layout with navigation
│   │   ├── Users/
│   │   │   ├── Users.jsx              # User management
│   │   │   └── UserModal.jsx          # User create/edit modal
│   │   ├── Roles/
│   │   │   ├── Roles.jsx              # Role management
│   │   │   └── RoleModal.jsx          # Role create/edit modal
│   │   ├── Plugins/
│   │   │   ├── Plugins.jsx            # Plugin management
│   │   │   └── PluginConfigModal.jsx  # Plugin configuration
│   │   └── Stock/
│   │       ├── StockInventory.jsx     # Inventory management
│   │       └── StockItemModal.jsx     # Item create/edit modal
│   ├── services/
│   │   └── api.js                     # API service layer
│   ├── App.jsx                        # Main app component
│   ├── main.jsx                       # App entry point
│   └── index.css                      # Global styles
├── index.html                         # HTML template
├── vite.config.js                     # Vite configuration
├── tailwind.config.js                 # Tailwind configuration
├── postcss.config.js                  # PostCSS configuration
└── package.json                       # Dependencies
```

## API Integration

The frontend communicates with the Flask backend via REST API endpoints. The proxy is configured in `vite.config.js` to forward `/api` requests to `http://localhost:5000`.

### Available Services

- **authService**: Authentication (login, logout, get current user)
- **userService**: User CRUD operations and role assignment
- **roleService**: Role CRUD operations and permission management
- **pluginService**: Plugin management (enable, disable, configure, reload)
- **stockService**: Stock inventory CRUD and statistics

### Authentication

The application uses JWT tokens stored in `localStorage`. The token is automatically included in all API requests via Axios interceptors.

## Features by Page

### Dashboard
- Overview statistics (users, roles, plugins, inventory)
- Inventory summary with total value and low stock alerts
- Current user profile information

### User Management
- List all users with pagination
- Create, edit, and delete users
- Assign/remove roles from users
- View user status (active/inactive)

### Role Management
- View all roles in card layout
- Create custom roles with permissions
- Edit role permissions
- Delete non-system roles
- JSON permission structure support

### Plugin Management
- List all plugins with status
- Enable/disable plugins
- Configure plugin settings (form or JSON editor)
- Reload active plugins
- Discover new plugins

### Stock Inventory
- Full inventory list with item details
- Real-time statistics (items, quantity, value, low stock)
- Create, edit, and delete items
- Low stock warnings
- SKU tracking

## Customization

### Changing API URL

Edit `vite.config.js` to change the backend URL:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://your-backend-url:port',
        changeOrigin: true,
      }
    }
  }
})
```

### Styling

The application uses Tailwind CSS. You can customize the theme in `tailwind.config.js`:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        // Add custom colors
      },
    },
  },
}
```

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure the Flask backend has CORS enabled:
```python
from flask_cors import CORS
CORS(app)
```

### API Connection Issues
- Verify the Flask backend is running on `http://localhost:5000`
- Check the proxy configuration in `vite.config.js`
- Verify the API endpoints in `src/services/api.js`

### Authentication Issues
- Clear `localStorage` and try logging in again
- Check if JWT token is valid in browser DevTools > Application > Local Storage
- Verify backend JWT configuration

## License

This project is part of the Flask MVC application with plugin architecture.
