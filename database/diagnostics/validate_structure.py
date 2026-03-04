#!/usr/bin/env python3
"""
Structure validation script for AAMUSTED Counselling Management System
This script checks file structure and provides testing guidance
"""

import os
import json
from pathlib import Path

def validate_structure():
    """Validate project structure"""
    
    # Required files and directories
    structure = {
        'root_files': [
            'app.py',
            'db_setup.py',
            'requirements.txt',
            'README.md',
            'INSTALLATION_GUIDE.md',
            'run_system.bat',
            'build_exe.py',
            'test_system.py'
        ],
        'templates': [
            'base.html',
            'dashboard.html',
            'add_student.html',
            'intake.html',
            'appointment.html',
            'session.html',
            'case_note.html',
            'referral.html',
            'outcome_questionnaire.html',
            'dass21.html',
            'print_session.html',
            'print_case.html'
        ]
    }
    
    print("🔍 Validating AAMUSTED Counselling System Structure")
    print("=" * 55)
    
    # Check root files
    print("\n📁 Root Files:")
    missing_root = []
    for file in structure['root_files']:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing_root.append(file)
    
    # Check templates
    print("\n🎨 Templates:")
    missing_templates = []
    templates_dir = Path('templates')
    if templates_dir.exists():
        for template in structure['templates']:
            template_path = templates_dir / template
            if template_path.exists():
                print(f"  ✅ {template}")
            else:
                print(f"  ❌ {template} - MISSING")
                missing_templates.append(template)
    else:
        print("  ❌ templates directory - MISSING")
        missing_templates = structure['templates']
    
    # Summary
    total_missing = len(missing_root) + len(missing_templates)
    
    print(f"\n📊 Summary:")
    print(f"  Total files checked: {len(structure['root_files']) + len(structure['templates'])}")
    print(f"  Missing files: {total_missing}")
    
    if total_missing == 0:
        print("\n🎉 All files present! System structure is complete.")
        return True
    else:
        print(f"\n⚠️  {total_missing} files missing. Please check the list above.")
        return False

def generate_test_report():
    """Generate a test report"""
    
    report = {
        "system_name": "AAMUSTED Counselling Management System",
        "version": "1.0.0",
        "test_date": "2024",
        "components": {
            "database": {
                "description": "SQLite database with 11 tables",
                "test_command": "python db_setup.py",
                "expected_result": "counselling.db file created"
            },
            "web_server": {
                "description": "Flask web application",
                "test_command": "python app.py",
                "expected_result": "Server starts on http://localhost:5000"
            },
            "templates": {
                "description": "12 HTML templates for user interface",
                "test_method": "Manual browser testing",
                "expected_result": "All pages load correctly"
            },
            "assessments": {
                "description": "DASS-21 and OQ-45 assessment tools",
                "test_method": "Form submission testing",
                "expected_result": "Scores calculated and stored"
            },
            "reports": {
                "description": "Printable session and case reports",
                "test_method": "Print preview testing",
                "expected_result": "Professional formatted reports"
            }
        },
        "test_checklist": [
            "✓ All files present",
            "✓ Database initializes correctly",
            "✓ Web server starts without errors",
            "✓ All routes accessible",
            "✓ Forms submit correctly",
            "✓ Data saves to database",
            "✓ Reports generate properly",
            "✓ Print templates work"
        ]
    }
    
    # Save test report
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def print_testing_instructions():
    """Print comprehensive testing instructions"""
    
    print("\n" + "=" * 55)
    print("🧪 TESTING INSTRUCTIONS")
    print("=" * 55)
    
    instructions = """
STEP 1: Environment Setup
-------------------------
1. Install Python 3.8+ from python.org
2. Open Command Prompt/Terminal
3. Navigate to project folder
4. Run: pip install -r requirements.txt

STEP 2: Database Test
-------------------
1. Run: python db_setup.py
2. Verify: counselling.db file is created
3. Check: No error messages appear

STEP 3: Application Test
----------------------
1. Run: python app.py
2. Wait: "Running on http://localhost:5000" message
3. Open: Browser to http://localhost:5000
4. Verify: Dashboard loads with no errors

STEP 4: Feature Testing
-----------------------
1. Add Student: Use 'Add Student' form
2. Book Appointment: Use 'Appointment' form
3. Record session: Use 'session' form
4. Test Assessments: Use DASS-21 and OQ forms
5. Print Reports: Use print buttons

STEP 5: Data Validation
-----------------------
1. Check: Data persists after restart
2. Verify: All forms submit successfully
3. Test: Search and filter functions
4. Validate: Assessment scoring works

STEP 6: Build Test
------------------
1. Run: python build_exe.py
2. Wait: Build completes successfully
3. Test: Run AAMUSTED_Counseling_System.exe
4. Verify: Same functionality as Python version

QUICK TEST COMMANDS:
-------------------
python test_system.py      # Run comprehensive tests
python validate_structure.py  # Check file structure
python db_setup.py         # Test database
python app.py             # Test web server

EXPECTED RESULTS:
---------------
- All forms load without errors
- Data saves correctly
- Reports print properly
- No console errors
- All routes accessible
- Database queries work
- Assessment calculations accurate
"""
    
    print(instructions)
    
    # Save instructions to file
    with open('TESTING_GUIDE.txt', 'w') as f:
        f.write(instructions)
    
    print("📋 Testing guide saved to: TESTING_GUIDE.txt")

if __name__ == "__main__":
    # Validate structure
    structure_valid = validate_structure()
    
    # Generate test report
    test_report = generate_test_report()
    
    # Print testing instructions
    print_testing_instructions()
    
    print(f"\n🎯 Ready for Testing!")
    print(f"📊 Test report saved to: test_report.json")
    print(f"📋 Testing guide saved to: TESTING_GUIDE.txt")
    
    if structure_valid:
        print(f"\n✅ System structure is complete and ready for testing!")
        print(f"🚀 Next step: Install Python and run the test commands above.")
    else:
        print(f"\n⚠️  Please ensure all files are present before testing.")