# database.py

import mysql.connector
from flask import current_app, g
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def init_db(app):
    """Initialize database connection"""

    # Load database configuration from environment variables
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'ODBC'),
        'password': os.getenv('DB_PASSWORD', 'schema123'),
        'database': os.getenv('DB_NAME', 'flask_crud'),
    }
    
    app.config['db_config'] = db_config

    # Define a teardown function to close the database connection
    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

def get_db():
    """Get or create a new database connection"""
    if 'db' not in g:
        db_config = current_app.config['db_config']
        g.db = mysql.connector.connect(**db_config)
    return g.db