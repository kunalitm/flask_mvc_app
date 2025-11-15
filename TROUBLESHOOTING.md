# Troubleshooting Guide

## Login Issues

### Problem: "Invalid username or password" error

**Solution 1: Reset Admin User Password**

Run the admin reset script:
```bash
python reset_admin.py
```

This will:
- Check if admin user exists
- Create admin user if missing
- Reset password to `admin123`
- Ensure user is active

**Solution 2: Verify Backend is Running**

Make sure the Flask backend is running on port 5000:
```bash
python run.py
```

You should see output like:
```
* Running on http://127.0.0.1:5000
```

**Solution 3: Test Login via API**

Test the login endpoint directly:
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

If successful, you'll get a JSON response with a token.

### Problem: Frontend not connecting to backend

**Check CORS Settings**

The backend needs to allow CORS for the frontend. Verify `app/__init__.py` has:
```python
from flask_cors import CORS
CORS(app)
```

**Check Proxy Configuration**

Verify `frontend/vite.config.js` has the proxy configured:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

**Verify Both Servers Are Running**

Backend (port 5000):
```bash
curl http://localhost:5000/api/users/
```

Frontend (port 3000):
```bash
curl http://localhost:3000
```

## Database Issues

### Problem: No tables in database

**Solution: Delete and recreate database**

```bash
# Stop the backend
# Delete the database
rm instance/app.db

# Start backend to recreate
python run.py
```

The database will be automatically created with:
- Default roles (admin, user, guest)
- Admin user (username: admin, password: admin123)

### Problem: Admin user missing

Run the reset script:
```bash
python reset_admin.py
```

### Check Database Contents

Use the check_db.py script:
```bash
python check_db.py
```

This shows all tables and row counts.

## Frontend Issues

### Problem: Frontend won't start

**Install Dependencies**

```bash
cd frontend
npm install
```

**Clear Cache and Reinstall**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Check Node Version**

```bash
node --version  # Should be 16+
```

### Problem: "Cannot find module" errors

Reinstall dependencies:
```bash
cd frontend
npm install
```

### Problem: API requests failing

**Check Browser Console**

Open DevTools (F12) and check:
1. Console for errors
2. Network tab for failed requests
3. Application tab > Local Storage for token

**Clear localStorage**

In browser console:
```javascript
localStorage.clear()
```

Then try logging in again.

## Common Error Messages

### Backend Errors

**"ModuleNotFoundError: No module named 'flask_bcrypt'"**

Install missing dependencies:
```bash
pip install -r requirements.txt
```

**"sqlalchemy.exc.OperationalError: no such table"**

Database not initialized. Delete and recreate:
```bash
rm instance/app.db
python run.py
```

**"Address already in use"**

Port 5000 is in use. Kill the process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Frontend Errors

**"ECONNREFUSED" when trying to connect to API**

Backend is not running. Start it:
```bash
python run.py
```

**"401 Unauthorized" on all requests**

Token expired or invalid. Logout and login again, or clear localStorage:
```javascript
localStorage.clear()
```

**CORS errors in browser console**

Backend needs CORS enabled. Check `app/__init__.py` for CORS configuration.

## Quick Fixes

### Complete Reset

1. **Stop both servers** (Ctrl+C in both terminals)

2. **Reset database:**
   ```bash
   rm instance/app.db
   ```

3. **Start backend:**
   ```bash
   python run.py
   ```

4. **Reset admin user:**
   ```bash
   python reset_admin.py
   ```

5. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Login:**
   - Navigate to http://localhost:3000
   - Username: `admin`
   - Password: `admin123`

### Verify Everything Works

Run these commands to verify setup:

1. **Check backend:**
   ```bash
   curl http://localhost:5000/api/users/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```
   Should return a token.

2. **Check frontend:**
   ```bash
   curl http://localhost:3000
   ```
   Should return HTML.

3. **Check database:**
   ```bash
   python check_db.py
   ```
   Should show tables with data.

## Getting Help

If you're still experiencing issues:

1. Check the console output for both servers
2. Check browser DevTools console for frontend errors
3. Verify all prerequisites are installed:
   - Python 3.8+
   - Node.js 16+
   - pip packages from requirements.txt
   - npm packages from frontend/package.json

## Useful Commands

```bash
# Backend
python run.py                    # Start backend
python reset_admin.py            # Reset admin user
python check_db.py               # Check database

# Frontend
cd frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server
npm run build                    # Production build

# Quick start both
./start-dev.sh                   # Linux/Mac
start-dev.bat                    # Windows

# Check ports
netstat -an | grep 5000         # Linux/Mac
netstat -an | findstr 5000      # Windows
```

## Login Credentials

**Default Admin User:**
- Username: `admin`
- Password: `admin123`

**IMPORTANT:** Change this password in production!

## Testing the Setup

After starting both servers, you should be able to:

1. ✅ Access frontend at http://localhost:3000
2. ✅ See login page
3. ✅ Login with admin/admin123
4. ✅ See dashboard with statistics
5. ✅ Navigate to Users, Roles, Plugins, Inventory pages
6. ✅ Create, edit, delete users
7. ✅ Manage roles and permissions
8. ✅ Enable/disable plugins
9. ✅ Add inventory items

If any of these fail, refer to the relevant section above.
