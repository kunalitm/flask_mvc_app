"""
User controller with RESTful API endpoints
"""
from flask import Blueprint, request, jsonify, g
from app import db
from app.models.user import User
from app.models.role import Role
from app.utils.rbac import login_required, role_required, create_token
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('users', __name__)


@user_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint

    Request:
        {
            "username": "admin",
            "password": "admin123"
        }

    Response:
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com"
            }
        }
    """
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'User account is inactive'}), 401

    # Create token
    token = create_token(user.id, user.username)

    return jsonify({
        'token': token,
        'user': user.to_dict(include_roles=True)
    }), 200


@user_bp.route('/', methods=['GET'])
@login_required
def get_users():
    """
    Get all users (paginated)

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)

    Response:
        {
            "users": [...],
            "total": 100,
            "page": 1,
            "per_page": 20,
            "pages": 5
        }
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [user.to_dict(include_roles=True) for user in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """
    Get user by ID

    Response:
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "roles": [...]
        }
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict(include_roles=True)), 200


@user_bp.route('/', methods=['POST'])
@role_required('admin')
def create_user():
    """
    Create a new user

    Request:
        {
            "username": "newuser",
            "email": "user@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "role_ids": [2]
        }

    Response:
        {
            "message": "User created successfully",
            "user": {...}
        }
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        # Add roles
        if 'role_ids' in data:
            for role_id in data['role_ids']:
                role = Role.query.get(role_id)
                if role:
                    user.add_role(role)

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(include_roles=True)
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username or email already exists'}), 409


@user_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """
    Update user information

    Request:
        {
            "email": "newemail@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "is_active": true
        }

    Response:
        {
            "message": "User updated successfully",
            "user": {...}
        }
    """
    user = User.query.get_or_404(user_id)

    # Check permissions: users can update themselves, admins can update anyone
    if g.current_user.id != user_id and not g.current_user.has_role('admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    data = request.get_json()

    try:
        # Update fields
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        # Only admins can change active status
        if 'is_active' in data and g.current_user.has_role('admin'):
            user.is_active = data['is_active']

        # Only admins can change password for other users
        if 'password' in data:
            if g.current_user.id == user_id or g.current_user.has_role('admin'):
                user.set_password(data['password'])

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict(include_roles=True)
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 409


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """
    Delete a user

    Response:
        {
            "message": "User deleted successfully"
        }
    """
    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    if user.id == g.current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/<int:user_id>/roles', methods=['POST'])
@role_required('admin')
def assign_role(user_id):
    """
    Assign role to user

    Request:
        {
            "role_id": 2
        }

    Response:
        {
            "message": "Role assigned successfully",
            "user": {...}
        }
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data.get('role_id'):
        return jsonify({'error': 'role_id is required'}), 400

    role = Role.query.get_or_404(data['role_id'])
    user.add_role(role)
    db.session.commit()

    return jsonify({
        'message': 'Role assigned successfully',
        'user': user.to_dict(include_roles=True)
    }), 200


@user_bp.route('/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@role_required('admin')
def remove_role(user_id, role_id):
    """
    Remove role from user

    Response:
        {
            "message": "Role removed successfully",
            "user": {...}
        }
    """
    user = User.query.get_or_404(user_id)
    role = Role.query.get_or_404(role_id)

    user.remove_role(role)
    db.session.commit()

    return jsonify({
        'message': 'Role removed successfully',
        'user': user.to_dict(include_roles=True)
    }), 200


@user_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current authenticated user

    Response:
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "roles": [...]
        }
    """
    return jsonify(g.current_user.to_dict(include_roles=True)), 200
