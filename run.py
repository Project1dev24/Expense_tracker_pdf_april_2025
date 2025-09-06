#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'app.py'

# Import and run the app
from app import app

if __name__ == '__main__':
    # Run the application
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = 5003  # Use a fixed port
    app.run(debug=debug, host='127.0.0.1', port=port)