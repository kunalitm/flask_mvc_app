"""
Application entry point

Run the Flask application with: python run.py
"""
import os
from dotenv import load_dotenv
from app import create_app
from app.config.settings import config

# Load environment variables from .env file
load_dotenv()

# Get environment from environment variable or default to development
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config.get(env, config['default']))

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Run the application
    print(f"Starting Flask MVC Plugin Application in {env} mode...")
    print(f"Server running on http://localhost:{port}")
    print(f"\nAPI Documentation available at /api/docs")
    print(f"\nDefault admin credentials:")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"\nPress CTRL+C to stop the server\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )
