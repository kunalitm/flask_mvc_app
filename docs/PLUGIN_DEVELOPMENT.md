# Plugin Development Guide

Complete guide for developing plugins for the Flask MVC Plugin Architecture.

## Plugin Basics

A plugin is a self-contained module that extends the application's functionality. Plugins follow a standard lifecycle and interface.

## Plugin Lifecycle

1. **Discovery** - Plugin manager scans plugin directory
2. **Loading** - Plugin module is imported
3. **Initialization** - Plugin's `initialize()` method is called
4. **Enabling** - Plugin's `enable()` and `on_enable()` methods are called
5. **Runtime** - Plugin is active and serving requests
6. **Disabling** - Plugin's `disable()` and `on_disable()` methods are called
7. **Unloading** - Plugin is removed from memory

## Creating a Plugin

### Step 1: Create Plugin Directory

```bash
mkdir -p app/plugins/my_plugin
touch app/plugins/my_plugin/__init__.py
touch app/plugins/my_plugin/plugin.py
```

### Step 2: Implement Plugin Class

Edit `app/plugins/my_plugin/plugin.py`:

```python
from app.plugins.base.base_plugin import BasePlugin
from flask import Blueprint, jsonify, request
from app.utils.rbac import login_required, role_required

class MyPlugin(BasePlugin):
    """
    My custom plugin
    """

    @property
    def name(self):
        """Unique plugin identifier"""
        return "my_plugin"

    @property
    def version(self):
        """Plugin version"""
        return "1.0.0"

    @property
    def description(self):
        """Plugin description"""
        return "My awesome plugin that does amazing things"

    @property
    def author(self):
        """Plugin author"""
        return "Your Name"

    def initialize(self):
        """Initialize the plugin"""
        if not super().initialize():
            return False

        # Custom initialization logic
        self.logger.info("Initializing my plugin")

        # Load configuration
        self.api_key = self.get_config('api_key', 'default-key')

        return True

    def on_enable(self):
        """Called when plugin is enabled"""
        self.logger.info("My plugin is being enabled")

        # Register routes
        if self.app:
            self.register_blueprints(self.app)

        # Start background tasks if needed
        # self.start_background_worker()

    def on_disable(self):
        """Called when plugin is disabled"""
        self.logger.info("My plugin is being disabled")

        # Save state
        self.set_config('api_key', self.api_key)

        # Stop background tasks if needed
        # self.stop_background_worker()

    def register_blueprints(self, app):
        """Register Flask blueprints"""
        bp = self._create_blueprint()

        if bp.name not in app.blueprints:
            app.register_blueprint(bp, url_prefix='/api/my_plugin')
            self.logger.info("Routes registered at /api/my_plugin")

    def _create_blueprint(self):
        """Create the plugin blueprint"""
        bp = Blueprint('my_plugin', __name__)
        plugin = self

        @bp.route('/hello', methods=['GET'])
        @login_required
        def hello():
            """Public endpoint"""
            return jsonify({
                'message': 'Hello from my plugin!',
                'version': plugin.version
            })

        @bp.route('/config', methods=['GET'])
        @role_required('admin')
        def get_config():
            """Admin-only endpoint"""
            return jsonify({
                'api_key': plugin.api_key
            })

        return bp
```

### Step 3: Add Plugin Initialization

Edit `app/plugins/my_plugin/__init__.py`:

```python
"""
My Plugin
"""
from app.plugins.my_plugin.plugin import MyPlugin

__all__ = ['MyPlugin']
```

## Plugin Structure Best Practices

```
my_plugin/
├── __init__.py          # Plugin package initialization
├── plugin.py            # Main plugin class
├── models.py            # Plugin-specific models (optional)
├── services.py          # Business logic (optional)
├── utils.py             # Utility functions (optional)
└── templates/           # Templates if needed (optional)
```

## Advanced Features

### Using Database Models

```python
from app import db

class MyPluginModel(db.Model):
    """Plugin-specific model"""
    __tablename__ = 'my_plugin_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # ... more fields

class MyPlugin(BasePlugin):
    def initialize(self):
        if super().initialize():
            # Create tables
            with self.app.app_context():
                db.create_all()
            return True
        return False
```

### Background Tasks

```python
import threading
import time

class MyPlugin(BasePlugin):
    def __init__(self, app=None, config=None):
        super().__init__(app, config)
        self.worker_thread = None
        self.running = False

    def on_enable(self):
        super().on_enable()
        self.start_worker()

    def on_disable(self):
        super().on_disable()
        self.stop_worker()

    def start_worker(self):
        """Start background worker"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def stop_worker(self):
        """Stop background worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()

    def _worker(self):
        """Background worker logic"""
        while self.running:
            # Do background work
            self.logger.info("Background task running")
            time.sleep(60)  # Run every minute
```

### Plugin Configuration

```python
class MyPlugin(BasePlugin):
    def initialize(self):
        if super().initialize():
            # Get configuration with defaults
            self.max_items = self.get_config('max_items', 100)
            self.api_endpoint = self.get_config('api_endpoint', 'https://api.example.com')

            # Validate configuration
            if not self.api_endpoint:
                self.logger.error("API endpoint not configured")
                return False

            return True
        return False

    def on_disable(self):
        # Save configuration
        self.set_config('max_items', self.max_items)
        self.set_config('api_endpoint', self.api_endpoint)
```

### External API Integration

```python
import requests

class MyPlugin(BasePlugin):
    def __init__(self, app=None, config=None):
        super().__init__(app, config)
        self.api_client = None

    def initialize(self):
        if super().initialize():
            # Initialize API client
            api_key = self.get_config('api_key')
            self.api_client = requests.Session()
            self.api_client.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
            return True
        return False

    def fetch_data(self):
        """Fetch data from external API"""
        try:
            response = self.api_client.get('https://api.example.com/data')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API error: {e}")
            return None
```

## Plugin Events and Hooks

You can extend the plugin system with custom events:

```python
class EventPlugin(BasePlugin):
    """Plugin with event system"""

    def __init__(self, app=None, config=None):
        super().__init__(app, config)
        self.listeners = {}

    def on(self, event_name, callback):
        """Register event listener"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def emit(self, event_name, data=None):
        """Emit event"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
```

## Testing Plugins

Create `tests/test_my_plugin.py`:

```python
import pytest
from app import create_app
from app.config.settings import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_plugin_loaded(app):
    """Test plugin is loaded"""
    plugin = app.plugin_manager.get_plugin('my_plugin')
    assert plugin is not None
    assert plugin.name == 'my_plugin'

def test_plugin_endpoint(client):
    """Test plugin endpoint"""
    response = client.get('/api/my_plugin/hello')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
```

## Plugin Configuration Schema

Create a configuration schema for your plugin:

```python
PLUGIN_CONFIG_SCHEMA = {
    'api_key': {
        'type': 'string',
        'required': True,
        'description': 'API key for external service'
    },
    'max_items': {
        'type': 'integer',
        'default': 100,
        'description': 'Maximum number of items to process'
    },
    'enabled_features': {
        'type': 'array',
        'default': [],
        'description': 'List of enabled features'
    }
}
```

## Error Handling

```python
class MyPlugin(BasePlugin):
    def on_enable(self):
        try:
            # Plugin logic
            self._setup_resources()
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable plugin: {e}")
            # Cleanup
            self._cleanup_resources()
            return False

    def _setup_resources(self):
        """Setup plugin resources"""
        # May raise exceptions
        pass

    def _cleanup_resources(self):
        """Cleanup plugin resources"""
        # Should not raise exceptions
        try:
            # Cleanup logic
            pass
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
```

## Plugin Dependencies

If your plugin depends on other plugins:

```python
class MyPlugin(BasePlugin):
    DEPENDENCIES = ['other_plugin']

    def initialize(self):
        if not super().initialize():
            return False

        # Check dependencies
        for dep in self.DEPENDENCIES:
            if not self.app.plugin_manager.get_plugin(dep):
                self.logger.error(f"Missing dependency: {dep}")
                return False

        return True
```

## Publishing Your Plugin

1. Create a separate repository
2. Add comprehensive documentation
3. Include example configuration
4. Provide installation instructions
5. Add tests
6. Version your plugin properly

## Best Practices

1. **Logging** - Use `self.logger` for all logging
2. **Configuration** - Use plugin config system
3. **Error Handling** - Handle errors gracefully
4. **Resource Cleanup** - Clean up in `on_disable()`
5. **Security** - Use RBAC decorators
6. **Documentation** - Document all endpoints
7. **Testing** - Write comprehensive tests
8. **Versioning** - Follow semantic versioning

## Example Plugins

Check these example plugins:

- **stock_plugin** - Inventory management (included)
- Create your own and share!
