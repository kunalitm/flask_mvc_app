"""
Role controller with RESTful API endpoints
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.role import Role
from app.utils.rbac import login_required, role_required
from sqlalchemy.exc import IntegrityError
import json

role_bp = Blueprint('roles', __name__)


@role_bp.route('/', methods=['GET'])
@login_required
def get_roles():
    """
    Get all roles
    ---
    tags:
      - Roles
    security:
      - Bearer: []
    responses:
      200:
        description: List of all roles
        schema:
          type: object
          properties:
            roles:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  description:
                    type: string
                  permissions:
                    type: array
                    items:
                      type: string
                  is_system:
                    type: boolean
      401:
        description: Authentication required
    """
    roles = Role.query.all()
    return jsonify({
        'roles': [role.to_dict(include_users=True) for role in roles]
    }), 200


@role_bp.route('/<int:role_id>', methods=['GET'])
@login_required
def get_role(role_id):
    """
    Get role by ID
    ---
    tags:
      - Roles
    security:
      - Bearer: []
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
        description: Role ID
    responses:
      200:
        description: Role details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            permissions:
              type: array
              items:
                type: string
            user_count:
              type: integer
      401:
        description: Authentication required
      404:
        description: Role not found
    """
    role = Role.query.get_or_404(role_id)
    return jsonify(role.to_dict(include_users=True)), 200


@role_bp.route('/', methods=['POST'])
@role_required('admin')
def create_role():
    """
    Create a new role
    ---
    tags:
      - Roles
    security:
      - Bearer: []
    parameters:
      - in: body
        name: role
        description: Role to create
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: moderator
            description:
              type: string
              example: Moderator role
            permissions:
              type: array
              items:
                type: string
              example: ["users.read", "users.update"]
    responses:
      201:
        description: Role created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            role:
              type: object
      400:
        description: Role name is required
      401:
        description: Authentication required
      403:
        description: Admin role required
      409:
        description: Role name already exists
    """
    data = request.get_json()

    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Role name is required'}), 400

    try:
        # Convert permissions list to JSON string
        permissions = data.get('permissions', [])
        permissions_json = json.dumps(permissions)

        role = Role(
            name=data['name'],
            description=data.get('description'),
            permissions=permissions_json,
            is_system=False  # Custom roles are never system roles
        )

        db.session.add(role)
        db.session.commit()

        return jsonify({
            'message': 'Role created successfully',
            'role': role.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Role name already exists'}), 409


@role_bp.route('/<int:role_id>', methods=['PUT'])
@role_required('admin')
def update_role(role_id):
    """
    Update role information

    Request:
        {
            "description": "Updated description",
            "permissions": ["users.read", "users.update", "users.delete"]
        }

    Response:
        {
            "message": "Role updated successfully",
            "role": {...}
        }
    """
    role = Role.query.get_or_404(role_id)

    # Prevent updating system roles
    if role.is_system:
        return jsonify({'error': 'Cannot modify system roles'}), 403

    data = request.get_json()

    try:
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        if 'permissions' in data:
            role.permissions = json.dumps(data['permissions'])

        db.session.commit()

        return jsonify({
            'message': 'Role updated successfully',
            'role': role.to_dict()
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Role name already exists'}), 409


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@role_required('admin')
def delete_role(role_id):
    """
    Delete a role

    Response:
        {
            "message": "Role deleted successfully"
        }
    """
    role = Role.query.get_or_404(role_id)

    # Prevent deleting system roles
    if role.is_system:
        return jsonify({'error': 'Cannot delete system roles'}), 403

    db.session.delete(role)
    db.session.commit()

    return jsonify({'message': 'Role deleted successfully'}), 200


@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@login_required
def get_role_permissions(role_id):
    """
    Get permissions for a role

    Response:
        {
            "role": "admin",
            "permissions": ["users.*", "roles.*", "plugins.*", "*"]
        }
    """
    role = Role.query.get_or_404(role_id)
    permissions = json.loads(role.permissions) if role.permissions else []

    return jsonify({
        'role': role.name,
        'permissions': permissions
    }), 200


@role_bp.route('/<int:role_id>/permissions', methods=['PUT'])
@role_required('admin')
def update_role_permissions(role_id):
    """
    Update permissions for a role

    Request:
        {
            "permissions": ["users.read", "users.update"]
        }

    Response:
        {
            "message": "Permissions updated successfully",
            "role": {...}
        }
    """
    role = Role.query.get_or_404(role_id)

    # Prevent updating system role permissions
    if role.is_system:
        return jsonify({'error': 'Cannot modify system role permissions'}), 403

    data = request.get_json()

    if 'permissions' not in data:
        return jsonify({'error': 'Permissions array is required'}), 400

    role.permissions = json.dumps(data['permissions'])
    db.session.commit()

    return jsonify({
        'message': 'Permissions updated successfully',
        'role': role.to_dict()
    }), 200
