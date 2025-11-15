"""
Stock Plugin - Demonstrates plugin architecture and lifecycle

This plugin provides a simple stock/inventory management system
and demonstrates how to:
- Implement the BasePlugin interface
- Register custom routes
- Use plugin configuration
- Handle plugin lifecycle (enable/disable)
"""
from flask import Blueprint, jsonify, request, g
from app.plugins.base.base_plugin import BasePlugin
from app.utils.rbac import login_required, role_required
import json


class StockPlugin(BasePlugin):
    """
    Stock management plugin demonstrating plugin capabilities
    """

    @property
    def name(self) -> str:
        return "stock_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Stock/Inventory management plugin - demonstrates plugin architecture"

    @property
    def author(self) -> str:
        return "MVC Plugin System"

    def __init__(self, app=None, config=None):
        super().__init__(app, config)
        self.blueprint = None
        # In-memory stock storage (in production, use database)
        self.stock_items = {}

        # Load stock from config if available
        if config and 'stock_items' in config:
            self.stock_items = config['stock_items']

    def initialize(self) -> bool:
        """Initialize the plugin"""
        if super().initialize():
            self.logger.info("Stock plugin initialized successfully")
            self.logger.info(f"Current stock items: {len(self.stock_items)}")
            return True
        return False

    def on_enable(self):
        """Called when plugin is enabled"""
        self.logger.info("Stock plugin enabled - registering routes")

        # Create and register blueprint
        if self.app:
            self.register_blueprints(self.app)

    def on_disable(self):
        """Called when plugin is disabled"""
        self.logger.info("Stock plugin disabled - saving state")

        # Save stock items to config before disabling
        self.set_config('stock_items', self.stock_items)

    def register_blueprints(self, app):
        """Register plugin blueprints"""
        if self.blueprint is None:
            self.blueprint = self._create_blueprint()

        # Check if blueprint is already registered
        if self.blueprint.name not in app.blueprints:
            app.register_blueprint(self.blueprint, url_prefix='/api/stock')
            self.logger.info("Stock plugin routes registered at /api/stock")

    def _create_blueprint(self):
        """Create the plugin blueprint with routes"""
        bp = Blueprint('stock_plugin', __name__)

        # Store reference to plugin instance
        plugin = self

        @bp.route('/items', methods=['GET'])
        @login_required
        def get_stock_items():
            """
            Get all stock items

            Response:
                {
                    "items": [
                        {
                            "id": "item1",
                            "name": "Product A",
                            "quantity": 100,
                            "price": 29.99
                        }
                    ]
                }
            """
            return jsonify({
                'items': list(plugin.stock_items.values())
            }), 200

        @bp.route('/items/<item_id>', methods=['GET'])
        @login_required
        def get_stock_item(item_id):
            """
            Get stock item by ID

            Response:
                {
                    "id": "item1",
                    "name": "Product A",
                    "quantity": 100,
                    "price": 29.99
                }
            """
            if item_id not in plugin.stock_items:
                return jsonify({'error': 'Item not found'}), 404

            return jsonify(plugin.stock_items[item_id]), 200

        @bp.route('/items', methods=['POST'])
        @role_required('admin')
        def create_stock_item():
            """
            Create a new stock item

            Request:
                {
                    "id": "item1",
                    "name": "Product A",
                    "quantity": 100,
                    "price": 29.99,
                    "description": "Product description"
                }

            Response:
                {
                    "message": "Stock item created successfully",
                    "item": {...}
                }
            """
            data = request.get_json()

            required_fields = ['id', 'name', 'quantity', 'price']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required'}), 400

            if data['id'] in plugin.stock_items:
                return jsonify({'error': 'Item ID already exists'}), 409

            item = {
                'id': data['id'],
                'name': data['name'],
                'quantity': data['quantity'],
                'price': data['price'],
                'description': data.get('description', ''),
                'created_by': g.current_user.username
            }

            plugin.stock_items[item['id']] = item

            return jsonify({
                'message': 'Stock item created successfully',
                'item': item
            }), 201

        @bp.route('/items/<item_id>', methods=['PUT'])
        @role_required('admin')
        def update_stock_item(item_id):
            """
            Update a stock item

            Request:
                {
                    "name": "Updated Product A",
                    "quantity": 150,
                    "price": 34.99
                }

            Response:
                {
                    "message": "Stock item updated successfully",
                    "item": {...}
                }
            """
            if item_id not in plugin.stock_items:
                return jsonify({'error': 'Item not found'}), 404

            data = request.get_json()
            item = plugin.stock_items[item_id]

            # Update fields
            if 'name' in data:
                item['name'] = data['name']
            if 'quantity' in data:
                item['quantity'] = data['quantity']
            if 'price' in data:
                item['price'] = data['price']
            if 'description' in data:
                item['description'] = data['description']

            item['updated_by'] = g.current_user.username

            return jsonify({
                'message': 'Stock item updated successfully',
                'item': item
            }), 200

        @bp.route('/items/<item_id>', methods=['DELETE'])
        @role_required('admin')
        def delete_stock_item(item_id):
            """
            Delete a stock item

            Response:
                {
                    "message": "Stock item deleted successfully"
                }
            """
            if item_id not in plugin.stock_items:
                return jsonify({'error': 'Item not found'}), 404

            del plugin.stock_items[item_id]

            return jsonify({
                'message': 'Stock item deleted successfully'
            }), 200

        @bp.route('/stats', methods=['GET'])
        @login_required
        def get_stock_stats():
            """
            Get stock statistics

            Response:
                {
                    "total_items": 10,
                    "total_quantity": 500,
                    "total_value": 5000.00,
                    "low_stock_items": 2
                }
            """
            total_items = len(plugin.stock_items)
            total_quantity = sum(item['quantity'] for item in plugin.stock_items.values())
            total_value = sum(item['quantity'] * item['price'] for item in plugin.stock_items.values())
            low_stock_items = sum(1 for item in plugin.stock_items.values() if item['quantity'] < 10)

            return jsonify({
                'total_items': total_items,
                'total_quantity': total_quantity,
                'total_value': round(total_value, 2),
                'low_stock_items': low_stock_items
            }), 200

        return bp
