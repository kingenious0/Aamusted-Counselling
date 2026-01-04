#!/usr/bin/env python
"""
AAMUSTED Counselling Management System - Run Script
Entry point for running the Flask web application
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("AAMUSTED Counselling Management System")
    print("=" * 60)
    print("\nStarting web server...")
    print("The system will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    print("-" * 60)
    
    # Log available routes for debugging
    print('\nRegistered routes:')
    for rule in app.url_map.iter_rules():
        print(f"  - {rule.endpoint}: {rule}")
    print("-" * 60)
    print()
    
    # Run the Flask application
    app.run(debug=True, host='127.0.0.1', port=5000)

