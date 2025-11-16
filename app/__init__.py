"""
Flask MVC Application with Plugin Architecture
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from app.config.settings import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    """
    Application factory pattern

    Args:
        config_class: Configuration class to use

    Returns:
        Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Import models
    from app.models import user, role, plugin, company, company_plugin

    # Register blueprints
    from app.controllers.user_controller import user_bp
    from app.controllers.role_controller import role_bp
    from app.controllers.plugin_controller import plugin_bp
    from app.controllers.company_controller import company_bp

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(role_bp, url_prefix='/api/roles')
    app.register_blueprint(plugin_bp, url_prefix='/api/plugins')
    app.register_blueprint(company_bp, url_prefix='/api/companies')

    # Create tables first
    with app.app_context():
        db.create_all()
        # Initialize default roles and admin user
        from app.utils.init_db import initialize_database
        initialize_database()

    # Initialize plugin manager after database is ready
    from app.plugins.manager.plugin_manager import PluginManager
    plugin_manager = PluginManager(app)
    app.plugin_manager = plugin_manager
    plugin_manager.load_plugins()

    return app
