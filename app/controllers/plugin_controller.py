"""
Plugin controller with RESTful API endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.plugin import Plugin
from app.utils.rbac import login_required, role_required

plugin_bp = Blueprint('plugins', __name__)


@plugin_bp.route('/', methods=['GET'])
@login_required
def get_plugins():
    """
    Get all plugins

    Response:
        {
            "plugins": [
                {
                    "id": 1,
                    "name": "stock_plugin",
                    "version": "1.0.0",
                    "description": "Stock management plugin",
                    "is_enabled": true,
                    "is_system": false
                }
            ]
        }
    """
    plugins = Plugin.query.all()
    return jsonify({
        'plugins': [plugin.to_dict() for plugin in plugins]
    }), 200


@plugin_bp.route('/<int:plugin_id>', methods=['GET'])
@login_required
def get_plugin(plugin_id):
    """
    Get plugin by ID

    Response:
        {
            "id": 1,
            "name": "stock_plugin",
            "version": "1.0.0",
            "description": "Stock management plugin",
            "is_enabled": true,
            "config": {...}
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)
    return jsonify(plugin.to_dict()), 200


@plugin_bp.route('/<int:plugin_id>/enable', methods=['POST'])
@role_required('admin')
def enable_plugin(plugin_id):
    """
    Enable a plugin

    Response:
        {
            "message": "Plugin enabled successfully",
            "plugin": {...}
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)

    # Use plugin manager to enable
    plugin_manager = current_app.plugin_manager
    success = plugin_manager.enable_plugin(plugin.name)

    if success:
        return jsonify({
            'message': 'Plugin enabled successfully',
            'plugin': plugin.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Failed to enable plugin'}), 500


@plugin_bp.route('/<int:plugin_id>/disable', methods=['POST'])
@role_required('admin')
def disable_plugin(plugin_id):
    """
    Disable a plugin

    Response:
        {
            "message": "Plugin disabled successfully",
            "plugin": {...}
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)

    if plugin.is_system:
        return jsonify({'error': 'Cannot disable system plugins'}), 403

    # Use plugin manager to disable
    plugin_manager = current_app.plugin_manager
    success = plugin_manager.disable_plugin(plugin.name)

    if success:
        return jsonify({
            'message': 'Plugin disabled successfully',
            'plugin': plugin.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Failed to disable plugin'}), 500


@plugin_bp.route('/<int:plugin_id>/config', methods=['GET'])
@login_required
def get_plugin_config(plugin_id):
    """
    Get plugin configuration

    Response:
        {
            "plugin": "stock_plugin",
            "config": {
                "api_key": "xxx",
                "max_items": 100
            }
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)
    return jsonify({
        'plugin': plugin.name,
        'config': plugin.get_config()
    }), 200


@plugin_bp.route('/<int:plugin_id>/config', methods=['PUT'])
@role_required('admin')
def update_plugin_config(plugin_id):
    """
    Update plugin configuration

    Request:
        {
            "config": {
                "api_key": "new_key",
                "max_items": 200
            }
        }

    Response:
        {
            "message": "Plugin configuration updated successfully",
            "plugin": {...}
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)
    data = request.get_json()

    if 'config' not in data:
        return jsonify({'error': 'Configuration object is required'}), 400

    plugin.set_config(data['config'])
    db.session.commit()

    # Update runtime plugin config if enabled
    plugin_manager = current_app.plugin_manager
    runtime_plugin = plugin_manager.get_plugin(plugin.name)
    if runtime_plugin:
        runtime_plugin.config = data['config']

    return jsonify({
        'message': 'Plugin configuration updated successfully',
        'plugin': plugin.to_dict()
    }), 200


@plugin_bp.route('/<int:plugin_id>/reload', methods=['POST'])
@role_required('admin')
def reload_plugin(plugin_id):
    """
    Reload a plugin

    Response:
        {
            "message": "Plugin reloaded successfully",
            "plugin": {...}
        }
    """
    plugin = Plugin.query.get_or_404(plugin_id)

    plugin_manager = current_app.plugin_manager
    success = plugin_manager.reload_plugin(plugin.name)

    if success:
        return jsonify({
            'message': 'Plugin reloaded successfully',
            'plugin': plugin.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Failed to reload plugin'}), 500


@plugin_bp.route('/discover', methods=['POST'])
@role_required('admin')
def discover_plugins():
    """
    Discover new plugins in the plugin directory

    Response:
        {
            "message": "Plugin discovery completed",
            "discovered": 3,
            "plugins": [...]
        }
    """
    plugin_manager = current_app.plugin_manager
    plugin_names = plugin_manager.discover_plugins()

    # Load newly discovered plugins
    newly_loaded = []
    for plugin_name in plugin_names:
        if plugin_name not in plugin_manager.plugins:
            plugin = plugin_manager.load_plugin(plugin_name)
            if plugin:
                newly_loaded.append(plugin.get_info())

    return jsonify({
        'message': 'Plugin discovery completed',
        'discovered': len(newly_loaded),
        'plugins': newly_loaded
    }), 200


@plugin_bp.route('/enabled', methods=['GET'])
@login_required
def get_enabled_plugins():
    """
    Get all enabled plugins

    Response:
        {
            "plugins": [...]
        }
    """
    plugins = Plugin.query.filter_by(is_enabled=True).all()
    return jsonify({
        'plugins': [plugin.to_dict() for plugin in plugins]
    }), 200
