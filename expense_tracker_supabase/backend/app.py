#!/usr/bin/env python3
"""
Main application file for Supabase expense tracker
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from backend.routes.auth import bp as auth_bp
from backend.routes.trips import bp as trips_bp
from backend.routes.expenses import bp as expenses_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    
    @app.route('/')
    def index():
        return '<h1>Expense Tracker with Supabase</h1><p><a href="/login">Login</a> | <a href="/register">Register</a> | <a href="/trips">My Trips</a></p>'
    
    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug, host='0.0.0.0', port=5003)