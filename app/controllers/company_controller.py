"""
Company controller with RESTful API endpoints for multi-tenant management
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.company import Company
from app.models.company_plugin import CompanyPlugin
from app.models.plugin import Plugin
from app.models.user import User
from app.utils.rbac import login_required, permission_required
import re

company_bp = Blueprint('companies', __name__)


def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


@company_bp.route('/', methods=['GET'])
@login_required
@permission_required('companies.read')
def get_companies():
    """
    Get all companies (Super admin only or users can see their own company)
    ---
    tags:
      - Companies
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: per_page
        type: integer
        default: 10
        description: Items per page
      - in: query
        name: include_stats
        type: boolean
        default: false
        description: Include statistics
    responses:
      200:
        description: List of companies
        schema:
          type: object
          properties:
            companies:
              type: array
              items:
                type: object
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    include_stats = request.args.get('include_stats', 'false').lower() == 'true'

    # Get current user from request context
    user = request.current_user

    # Super admin can see all companies, regular users only their own
    if user.is_super_admin:
        query = Company.query
    else:
        query = Company.query.filter_by(id=user.company_id)

    pagination = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'companies': [company.to_dict(include_stats=include_stats) for company in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page
    }), 200


@company_bp.route('/<int:company_id>', methods=['GET'])
@login_required
@permission_required('companies.read')
def get_company(company_id):
    """
    Get company by ID

    Response:
        {company_object}
    """
    user = request.current_user

    company = Company.query.get_or_404(company_id)

    # Check access: super admin or user from same company
    if not user.is_super_admin and user.company_id != company_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(company.to_dict(include_stats=True)), 200


@company_bp.route('/', methods=['POST'])
@login_required
@permission_required('companies.create')
def create_company():
    """
    Create a new company (Super admin only)
    ---
    tags:
      - Companies
    security:
      - Bearer: []
    parameters:
      - in: body
        name: company
        description: Company to create
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: ACME Corporation
            description:
              type: string
              example: Technology company
            email:
              type: string
              example: contact@acme.com
            phone:
              type: string
              example: +1234567890
            address:
              type: string
              example: 123 Main St, City
            max_users:
              type: integer
              example: 50
            settings:
              type: object
    responses:
      201:
        description: Company created successfully
        schema:
          type: object
      400:
        description: Missing required fields or company already exists
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
    """
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Company name is required'}), 400

    # Check if company already exists
    if Company.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Company with this name already exists'}), 400

    # Generate slug
    slug = slugify(data['name'])
    if Company.query.filter_by(slug=slug).first():
        slug = f"{slug}-{Company.query.count() + 1}"

    company = Company(
        name=data['name'],
        slug=slug,
        description=data.get('description'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        max_users=data.get('max_users', 10),
        settings=data.get('settings', {})
    )

    db.session.add(company)
    db.session.commit()

    return jsonify(company.to_dict()), 201


@company_bp.route('/<int:company_id>', methods=['PUT'])
@login_required
@permission_required('companies.update')
def update_company(company_id):
    """
    Update company

    Request:
        {
            "name": "Updated Name",
            "description": "Updated description",
            ...
        }

    Response:
        {company_object}
    """
    company = Company.query.get_or_404(company_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update fields
    if 'name' in data and data['name'] != company.name:
        if Company.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Company with this name already exists'}), 400
        company.name = data['name']
        company.slug = slugify(data['name'])

    if 'description' in data:
        company.description = data['description']
    if 'email' in data:
        company.email = data['email']
    if 'phone' in data:
        company.phone = data['phone']
    if 'address' in data:
        company.address = data['address']
    if 'max_users' in data:
        company.max_users = data['max_users']
    if 'is_active' in data:
        company.is_active = data['is_active']
    if 'settings' in data:
        company.settings = data['settings']

    db.session.commit()

    return jsonify(company.to_dict()), 200


@company_bp.route('/<int:company_id>', methods=['DELETE'])
@login_required
@permission_required('companies.delete')
def delete_company(company_id):
    """
    Delete company (Super admin only)

    Response:
        {"message": "Company deleted successfully"}
    """
    company = Company.query.get_or_404(company_id)

    # Check if company has users
    if company.users.count() > 0:
        return jsonify({'error': 'Cannot delete company with active users'}), 400

    db.session.delete(company)
    db.session.commit()

    return jsonify({'message': 'Company deleted successfully'}), 200


# Company-Plugin Management Endpoints

@company_bp.route('/<int:company_id>/plugins', methods=['GET'])
@login_required
@permission_required('plugins.read')
def get_company_plugins(company_id):
    """
    Get all plugins for a company
    ---
    tags:
      - Companies
      - Plugins
    security:
      - Bearer: []
    parameters:
      - in: path
        name: company_id
        type: integer
        required: true
        description: Company ID
    responses:
      200:
        description: List of plugins with company-specific status
        schema:
          type: object
          properties:
            plugins:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  company_status:
                    type: object
                    properties:
                      is_enabled:
                        type: boolean
                      installed_at:
                        type: string
                      config:
                        type: object
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
      404:
        description: Company not found
    """
    company = Company.query.get_or_404(company_id)

    # Get all plugins with company-specific status
    all_plugins = Plugin.query.all()
    result = []

    for plugin in all_plugins:
        company_plugin = CompanyPlugin.query.filter_by(
            company_id=company_id,
            plugin_id=plugin.id
        ).first()

        plugin_data = plugin.to_dict()
        if company_plugin:
            plugin_data['company_status'] = {
                'is_enabled': company_plugin.is_enabled,
                'installed_at': company_plugin.installed_at.isoformat() if company_plugin.installed_at else None,
                'config': company_plugin.config or {}
            }
        else:
            plugin_data['company_status'] = {
                'is_enabled': False,
                'installed_at': None,
                'config': {}
            }

        result.append(plugin_data)

    return jsonify({'plugins': result}), 200


@company_bp.route('/<int:company_id>/plugins/<int:plugin_id>/install', methods=['POST'])
@login_required
@permission_required('plugins.create')
def install_plugin_to_company(company_id, plugin_id):
    """
    Install/assign a plugin to a company

    Request:
        {
            "config": {plugin_specific_config}
        }

    Response:
        {company_plugin_object}
    """
    company = Company.query.get_or_404(company_id)
    plugin = Plugin.query.get_or_404(plugin_id)

    # Check if already installed
    company_plugin = CompanyPlugin.query.filter_by(
        company_id=company_id,
        plugin_id=plugin_id
    ).first()

    if company_plugin:
        return jsonify({'error': 'Plugin already installed for this company'}), 400

    data = request.get_json() or {}

    company_plugin = CompanyPlugin(
        company_id=company_id,
        plugin_id=plugin_id,
        is_enabled=False,
        config=data.get('config', {})
    )

    db.session.add(company_plugin)
    db.session.commit()

    return jsonify(company_plugin.to_dict()), 201


@company_bp.route('/<int:company_id>/plugins/<int:plugin_id>/enable', methods=['POST'])
@login_required
@permission_required('plugins.update')
def enable_company_plugin(company_id, plugin_id):
    """
    Enable a plugin for a company
    ---
    tags:
      - Companies
      - Plugins
    security:
      - Bearer: []
    parameters:
      - in: path
        name: company_id
        type: integer
        required: true
        description: Company ID
      - in: path
        name: plugin_id
        type: integer
        required: true
        description: Plugin ID
    responses:
      200:
        description: Plugin enabled successfully
        schema:
          type: object
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
      404:
        description: Plugin not installed for this company
    """
    company_plugin = CompanyPlugin.query.filter_by(
        company_id=company_id,
        plugin_id=plugin_id
    ).first()

    if not company_plugin:
        return jsonify({'error': 'Plugin not installed for this company'}), 404

    company_plugin.enable()
    db.session.commit()

    return jsonify(company_plugin.to_dict()), 200


@company_bp.route('/<int:company_id>/plugins/<int:plugin_id>/disable', methods=['POST'])
@login_required
@permission_required('plugins.update')
def disable_company_plugin(company_id, plugin_id):
    """
    Disable a plugin for a company

    Response:
        {company_plugin_object}
    """
    company_plugin = CompanyPlugin.query.filter_by(
        company_id=company_id,
        plugin_id=plugin_id
    ).first()

    if not company_plugin:
        return jsonify({'error': 'Plugin not installed for this company'}), 404

    company_plugin.disable()
    db.session.commit()

    return jsonify(company_plugin.to_dict()), 200


@company_bp.route('/<int:company_id>/plugins/<int:plugin_id>/config', methods=['GET'])
@login_required
@permission_required('plugins.read')
def get_company_plugin_config(company_id, plugin_id):
    """
    Get plugin configuration for a company

    Response:
        {"config": {config_object}}
    """
    company_plugin = CompanyPlugin.query.filter_by(
        company_id=company_id,
        plugin_id=plugin_id
    ).first_or_404()

    return jsonify({'config': company_plugin.config or {}}), 200


@company_bp.route('/<int:company_id>/plugins/<int:plugin_id>/config', methods=['PUT'])
@login_required
@permission_required('plugins.update')
def update_company_plugin_config(company_id, plugin_id):
    """
    Update plugin configuration for a company

    Request:
        {"config": {config_object}}

    Response:
        {"config": {config_object}}
    """
    company_plugin = CompanyPlugin.query.filter_by(
        company_id=company_id,
        plugin_id=plugin_id
    ).first_or_404()

    data = request.get_json()
    if not data or 'config' not in data:
        return jsonify({'error': 'Config is required'}), 400

    company_plugin.config = data['config']
    db.session.commit()

    return jsonify({'config': company_plugin.config}), 200


@company_bp.route('/<int:company_id>/users', methods=['GET'])
@login_required
@permission_required('users.read')
def get_company_users(company_id):
    """
    Get all users for a company

    Response:
        {"users": [{user_object}]}
    """
    company = Company.query.get_or_404(company_id)

    users = company.users.all()

    return jsonify({
        'users': [user.to_dict(include_roles=True) for user in users],
        'total': len(users),
        'max_users': company.max_users
    }), 200


@company_bp.route('/<int:company_id>/stats', methods=['GET'])
@login_required
@permission_required('companies.read')
def get_company_stats(company_id):
    """
    Get company statistics

    Response:
        {
            "user_count": N,
            "max_users": N,
            "plugin_count": N,
            "enabled_plugins": N
        }
    """
    company = Company.query.get_or_404(company_id)

    return jsonify({
        'user_count': company.users.count(),
        'max_users': company.max_users,
        'plugin_count': company.company_plugins.count(),
        'enabled_plugins': company.company_plugins.filter_by(is_enabled=True).count()
    }), 200
