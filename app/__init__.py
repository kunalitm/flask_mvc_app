"""
Flask MVC Application with Plugin Architecture
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from app.config.settings import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
swagger = Swagger()


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

    # Initialize Swagger API Documentation
    app.config['SWAGGER'] = {
        'title': 'Flask MVC Plugin API',
        'description': 'RESTful API for Flask MVC Plugin Application with multi-tenant support',
        'version': '1.0.0',
        'uiversion': 3,
        'specs_route': '/api/docs',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: Authorization: Bearer {token}'
            }
        },
        'tags': [
            {'name': 'Authentication', 'description': 'User authentication endpoints'},
            {'name': 'Users', 'description': 'User management operations'},
            {'name': 'Roles', 'description': 'Role-based access control'},
            {'name': 'Companies', 'description': 'Multi-tenant company management'},
            {'name': 'Plugins', 'description': 'Plugin management operations'}
        ]
    }

    swagger.init_app(app)

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
    import os
    skip_init = os.environ.get('SKIP_DB_INIT', '').lower() in ('1', 'true', 'yes')

    with app.app_context():
        db.create_all()
        # Initialize default roles and admin user (unless skipped for manual control)
        if not skip_init:
            from app.utils.init_db import initialize_database
            initialize_database()

    # Initialize plugin manager after database is ready
    from app.plugins.manager.plugin_manager import PluginManager
    plugin_manager = PluginManager(app)
    app.plugin_manager = plugin_manager
    plugin_manager.load_plugins()

    return app
