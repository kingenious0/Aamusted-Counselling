#!/usr/bin/env python3
"""
Test script for AAMUSTED Counselling Management System
This script validates the system components before packaging
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path

def test_database_setup():
    """Test database creation and structure"""
    print("🔍 Testing Database Setup...")
    
    try:
        # Create temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name
        
        # Test database creation
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Test table creation
        tables = [
            'Student', 'Counsellor', 'Appointment', 'session', 
            'CaseManagement', 'Referral', 'OutcomeQuestionnaire', 
            'DASS21', 'Issue', 'SessionIssue', 'Feedback'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"❌ Table {table} not found")
                return False
        
        conn.close()
        os.unlink(test_db_path)
        print("✅ Database structure validated")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_templates():
    """Validate template files"""
    print("🔍 Testing Templates...")
    
    required_templates = [
        'base.html', 'dashboard.html', 'add_student.html', 
        'intake.html', 'appointment.html', 'session.html',
        'case_note.html', 'referral.html', 'outcome_questionnaire.html',
        'dass21.html', 'print_session.html', 'print_case.html'
    ]
    
    templates_dir = Path('templates')
    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return False
    
    missing = []
    for template in required_templates:
        template_path = templates_dir / template
        if not template_path.exists():
            missing.append(template)
    
    if missing:
        print(f"❌ Missing templates: {missing}")
        return False
    
    print("✅ All templates validated")
    return True

def test_dependencies():
    """Check required dependencies"""
    print("🔍 Testing Dependencies...")
    
    required_modules = [
        'flask', 'sqlite3', 'datetime', 'json'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    
    print("✅ All dependencies available")
    return True

def test_routes():
    """Validate Flask routes"""
    print("🔍 Testing Application Routes...")
    
    expected_routes = [
        '/', '/dashboard', '/add_student', '/intake', '/appointment',
        '/session', '/case_note', '/referral', '/outcome_questionnaire',
        '/dass21', '/print_record'
    ]
    
    try:
        # Import app and check routes
        sys.path.insert(0, '.')
        from app import app
        
        with app.test_client() as client:
            for route in expected_routes:
                try:
                    response = client.get(route)
                    if response.status_code not in [200, 302]:  # 302 is redirect
                        print(f"❌ Route {route} returned {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ Route {route} error: {e}")
                    return False
        
        print("✅ All routes validated")
        return True
        
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False

def test_database_content():
    """Test database sample data"""
    print("🔍 Testing Database Content...")
    
    try:
        conn = sqlite3.connect(':memory:')
        
        # Read and execute db_setup.py content
        with open('db_setup.py', 'r') as f:
            setup_content = f.read()
        
        # Execute setup in memory database
        exec(setup_content, {'sqlite3': sqlite3, 'conn': conn})
        
        cursor = conn.cursor()
        
        # Test sample data
        cursor.execute("SELECT COUNT(*) FROM Issue")
        issue_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Counsellor")
        Counsellor_count = cursor.fetchone()[0]
        
        if issue_count > 0 and Counsellor_count > 0:
            print("✅ Sample data validated")
            conn.close()
            return True
        else:
            print("❌ Sample data missing")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database content test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 AAMUSTED Counselling System - Comprehensive Test")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_templates,
        test_database_setup,
        test_database_content,
        test_routes
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! System is ready for packaging.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Run tests
    success = run_comprehensive_test()
    
    if success:
        print("\n📋 Next Steps:")
        print("1. Install Python 3.8+ if not already installed")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python db_setup.py")
        print("4. Run: python app.py")
        print("5. Visit: http://localhost:5000")
        print("6. Or build executable: python build_exe.py")
    else:
        sys.exit(1)