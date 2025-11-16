"""
Role-Based Access Control (RBAC) decorators and utilities
"""
from functools import wraps
from flask import request, jsonify, g
from app.models.user import User
import jwt
from datetime import datetime, timedelta
import os


def create_token(user_id, username):
    """
    Create JWT token for user

    Args:
        user_id: User ID
        username: Username

    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    return jwt.encode(payload, secret_key, algorithm='HS256')


def decode_token(token):
    """
    Decode JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None if invalid
    """
    try:
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request():
    """
    Extract token from request headers

    Returns:
        Token string or None
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def login_required(f):
    """
    Decorator to require authentication

    Usage:
        @login_required
        def protected_route():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({'error': 'Authentication required', 'message': 'No token provided'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token', 'message': 'Token is invalid or expired'}), 401

        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Store user in both g and request for access in route
        g.current_user = user
        request.current_user = user

        return f(*args, **kwargs)

    return decorated_function


def role_required(*role_names):
    """
    Decorator to require specific roles

    Args:
        role_names: One or more role names required

    Usage:
        @role_required('admin')
        def admin_route():
            pass

        @role_required('admin', 'moderator')
        def multi_role_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user

            # Check if user has any of the required roles
            if not user.has_any_role(role_names):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires one of the following roles: {", ".join(role_names)}'
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def permission_required(permission):
    """
    Decorator to require specific permission

    Args:
        permission: Permission string required

    Usage:
        @permission_required('users.create')
        def create_user():
            pass
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user

            # Super admin has all permissions
            if user.is_super_admin:
                return f(*args, **kwargs)

            # Check permissions in user's roles
            import json
            has_permission = False

            for role in user.roles:
                permissions = json.loads(role.permissions) if role.permissions else []
                # Check for exact permission or wildcard
                if permission in permissions or '*' in permissions:
                    has_permission = True
                    break

                # Check for wildcard patterns (e.g., "users.*" matches "users.create")
                for perm in permissions:
                    if perm.endswith('.*'):
                        prefix = perm[:-2]
                        if permission.startswith(prefix + '.'):
                            has_permission = True
                            break

            if not has_permission:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'This action requires permission: {permission}'
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to require admin role

    Usage:
        @admin_required
        def admin_route():
            pass
    """
    return role_required('admin')(f)
