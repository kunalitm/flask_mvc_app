"""
Base plugin class that all plugins must inherit from
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class BasePlugin(ABC):
    """
    Base class for all plugins in the system

    All plugins must inherit from this class and implement the required methods.
    This provides a consistent interface for plugin lifecycle management.
    """

    def __init__(self, app=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin

        Args:
            app: Flask application instance
            config: Plugin configuration dictionary
        """
        self.app = app
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._enabled = False
        self._initialized = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (must be unique)"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass

    @property
    def author(self) -> str:
        """Plugin author (optional)"""
        return "Unknown"

    @property
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self._enabled

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized"""
        return self._initialized

    def initialize(self) -> bool:
        """
        Initialize the plugin

        Called when the plugin is first loaded.
        Override this method to perform initialization tasks.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.logger.info(f"Initializing plugin: {self.name}")
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin {self.name}: {str(e)}")
            return False

    def enable(self) -> bool:
        """
        Enable the plugin

        Called when the plugin is enabled by the user.
        Override this method to perform enable tasks.

        Returns:
            bool: True if enabling was successful, False otherwise
        """
        try:
            if not self._initialized:
                self.initialize()

            self.logger.info(f"Enabling plugin: {self.name}")
            self._enabled = True
            self.on_enable()
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable plugin {self.name}: {str(e)}")
            return False

    def disable(self) -> bool:
        """
        Disable the plugin

        Called when the plugin is disabled by the user.
        Override this method to perform disable tasks.

        Returns:
            bool: True if disabling was successful, False otherwise
        """
        try:
            self.logger.info(f"Disabling plugin: {self.name}")
            self._enabled = False
            self.on_disable()
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable plugin {self.name}: {str(e)}")
            return False

    def on_enable(self):
        """
        Called when plugin is enabled

        Override this method to perform tasks when the plugin is enabled.
        """
        pass

    def on_disable(self):
        """
        Called when plugin is disabled

        Override this method to perform cleanup when the plugin is disabled.
        """
        pass

    def register_routes(self, app):
        """
        Register Flask routes

        Override this method to register custom routes for the plugin.

        Args:
            app: Flask application instance
        """
        pass

    def register_blueprints(self, app):
        """
        Register Flask blueprints

        Override this method to register blueprints for the plugin.

        Args:
            app: Flask application instance
        """
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any):
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information

        Returns:
            Dictionary containing plugin information
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.is_enabled,
            'initialized': self.is_initialized
        }

    def __repr__(self):
        return f'<Plugin {self.name} v{self.version}>'
