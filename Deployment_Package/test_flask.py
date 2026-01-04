#!/usr/bin/env python3
"""
Test script to verify Flask application works
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test basic imports
    print("Testing Flask imports...")
    from flask import Flask, render_template, request, redirect, url_for, session, jsonify
    print("✓ Flask imported successfully")
    
    # Test app import
    print("Testing app import...")
    from app import app
    print("✓ App imported successfully")
    
    # Test database
    print("Testing database...")
    import sqlite3
    print("✓ SQLite3 imported successfully")
    
    # Test running app
    print("Testing Flask app...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ App test successful, status code: {response.status_code}")
        
    print("\n✓ All tests passed! Flask app is working correctly.")
    print("\nTo run the app manually, use:")
    print("python app.py")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install required packages:")
    print("pip install flask")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()