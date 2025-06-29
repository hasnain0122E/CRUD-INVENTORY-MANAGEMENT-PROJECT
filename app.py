from flask import Flask, redirect, url_for
from database import init_db
import os
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.items import items_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True

    # Configure Flask app
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    app.debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Database configuration
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_USER'] = os.getenv('DB_USER')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
    app.config['DB_NAME'] = os.getenv('DB_NAME')

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))  # Changed to login page
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(items_bp, url_prefix='/items')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)