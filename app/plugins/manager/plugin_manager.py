"""
Plugin Manager for dynamic plugin loading and management
"""
import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional
import logging

from app.plugins.base.base_plugin import BasePlugin
from app.models.plugin import Plugin as PluginModel
from app import db


class PluginManager:
    """
    Manages plugin lifecycle: loading, enabling, disabling, and unloading

    The PluginManager handles:
    - Discovery of available plugins
    - Dynamic loading of plugin modules
    - Plugin lifecycle management (enable/disable)
    - Plugin state persistence in database
    """

    def __init__(self, app=None):
        """
        Initialize the plugin manager

        Args:
            app: Flask application instance
        """
        self.app = app
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = logging.getLogger(__name__)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize with Flask application

        Args:
            app: Flask application instance
        """
        self.app = app
        self.plugin_dir = app.config.get('PLUGIN_DIR', Path(__file__).parent.parent)

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory

        Returns:
            List of plugin module names
        """
        plugin_modules = []
        plugin_dir = Path(self.plugin_dir)

        # Skip base and manager directories
        skip_dirs = {'base', 'manager', '__pycache__'}

        for item in plugin_dir.iterdir():
            if item.is_dir() and item.name not in skip_dirs:
                # Check if it has a plugin.py file
                plugin_file = item / 'plugin.py'
                if plugin_file.exists():
                    plugin_modules.append(item.name)

        self.logger.info(f"Discovered {len(plugin_modules)} plugins: {plugin_modules}")
        return plugin_modules

    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Load a plugin by name

        Args:
            plugin_name: Name of the plugin directory

        Returns:
            BasePlugin instance or None if loading failed
        """
        try:
            # Import the plugin module
            module_path = f'app.plugins.{plugin_name}.plugin'
            self.logger.info(f"Loading plugin from: {module_path}")

            module = importlib.import_module(module_path)

            # Find the plugin class (subclass of BasePlugin)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BasePlugin) and
                    obj is not BasePlugin):
                    plugin_class = obj
                    break

            if not plugin_class:
                self.logger.error(f"No plugin class found in {module_path}")
                return None

            # Get or create plugin configuration from database
            with self.app.app_context():
                plugin_model = PluginModel.query.filter_by(name=plugin_name).first()
                config = plugin_model.get_config() if plugin_model else {}

                # Instantiate the plugin
                plugin = plugin_class(app=self.app, config=config)

                # Initialize the plugin
                if plugin.initialize():
                    self.plugins[plugin.name] = plugin
                    self.logger.info(f"Successfully loaded plugin: {plugin.name}")

                    # Update or create database record
                    if not plugin_model:
                        plugin_model = PluginModel(
                            name=plugin.name,
                            version=plugin.version,
                            description=plugin.description,
                            author=plugin.author,
                            is_enabled=False
                        )
                        db.session.add(plugin_model)
                    else:
                        plugin_model.version = plugin.version
                        plugin_model.description = plugin.description
                        plugin_model.author = plugin.author

                    db.session.commit()

                    return plugin
                else:
                    self.logger.error(f"Failed to initialize plugin: {plugin.name}")
                    return None

        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            return None

    def load_plugins(self):
        """
        Discover and load all available plugins
        """
        plugin_names = self.discover_plugins()

        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)

        # Enable plugins that are marked as enabled in database
        self.restore_enabled_plugins()

    def restore_enabled_plugins(self):
        """
        Restore enabled state of plugins from database
        """
        with self.app.app_context():
            enabled_plugins = PluginModel.query.filter_by(is_enabled=True).all()

            for plugin_model in enabled_plugins:
                if plugin_model.name in self.plugins:
                    plugin = self.plugins[plugin_model.name]
                    if plugin.enable():
                        self.logger.info(f"Enabled plugin: {plugin.name}")
                    else:
                        self.logger.error(f"Failed to enable plugin: {plugin.name}")

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False

        plugin = self.plugins[plugin_name]

        if plugin.enable():
            # Update database
            with self.app.app_context():
                plugin_model = PluginModel.query.filter_by(name=plugin_name).first()
                if plugin_model:
                    plugin_model.enable()
                    db.session.commit()

            self.logger.info(f"Enabled plugin: {plugin_name}")
            return True
        else:
            self.logger.error(f"Failed to enable plugin: {plugin_name}")
            return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False

        plugin = self.plugins[plugin_name]

        if plugin.disable():
            # Update database
            with self.app.app_context():
                plugin_model = PluginModel.query.filter_by(name=plugin_name).first()
                if plugin_model:
                    plugin_model.disable()
                    db.session.commit()

            self.logger.info(f"Disabled plugin: {plugin_name}")
            return True
        else:
            self.logger.error(f"Failed to disable plugin: {plugin_name}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name

        Args:
            plugin_name: Name of the plugin

        Returns:
            BasePlugin instance or None
        """
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all loaded plugins

        Returns:
            Dictionary of plugin name to BasePlugin instance
        """
        return self.plugins.copy()

    def get_enabled_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all enabled plugins

        Returns:
            Dictionary of enabled plugins
        """
        return {name: plugin for name, plugin in self.plugins.items() if plugin.is_enabled}

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if successful, False otherwise
        """
        if plugin_name in self.plugins:
            # Disable and remove the plugin
            self.plugins[plugin_name].disable()
            del self.plugins[plugin_name]

        # Reload the plugin
        plugin = self.load_plugin(plugin_name)
        return plugin is not None
