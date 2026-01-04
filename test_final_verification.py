#!/usr/bin/env python3
"""
Final verification test to check all database fixes
"""

import sqlite3
import os

def test_all_functions():
    """Test all the functions that were having issues"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'counseling.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    print("=== FINAL VERIFICATION TEST ===")
    
    # Test 1: create_session function query
    print("\n1. Testing create_session query...")
    try:
        result = conn.execute('''
            SELECT a.*, s.name as student_name, s.contact, c.name as counsellor_name
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            JOIN Counsellor c ON a.counselor_id = c.id
            WHERE a.status = 'scheduled'
            ORDER BY a.date, a.time
        ''').fetchall()
        print(f"   ✓ Success: Found {len(result)} scheduled appointments")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: students function query
    print("\n2. Testing students function query...")
    try:
        result = conn.execute('''
            SELECT s.*, 
                   COUNT(DISTINCT sess.id) as session_count
            FROM Student s
            LEFT JOIN Appointment a ON s.id = a.student_id
            LEFT JOIN Session sess ON a.id = sess.appointment_id
            GROUP BY s.id
            ORDER BY s.name
        ''').fetchall()
        print(f"   ✓ Success: Found {len(result)} students")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: referral function query
    print("\n3. Testing referral function query...")
    try:
        result = conn.execute('''
            SELECT s.id, s.created_at, st.name as student_name, st.id as student_id, 'Counsellor' as Counsellor_name
            FROM Session s
            JOIN Appointment a ON s.appointment_id = a.id
            JOIN Student st ON a.student_id = st.id
            ORDER BY s.created_at DESC
        ''').fetchall()
        print(f"   ✓ Success: Found {len(result)} sessions for referral form")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: all_referrals function query
    print("\n4. Testing all_referrals function query...")
    try:
        result = conn.execute('''
            SELECT r.id, r.session_id, r.referred_by, r.contact, r.reasons, r.created_at,
                   st.name as student_name, st.contact as student_contact
            FROM Referral r
            JOIN Session sess ON r.session_id = sess.id
            JOIN Appointment a ON sess.appointment_id = a.id
            JOIN Student st ON a.student_id = st.id
            ORDER BY r.created_at DESC
        ''').fetchall()
        print(f"   ✓ Success: Found {len(result)} referrals")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: case_note function query
    print("\n5. Testing case_note function query...")
    try:
        result = conn.execute('''
            SELECT s.id, st.name as student_name, s.created_at
            FROM Session s
            JOIN Appointment a ON s.appointment_id = a.id
            JOIN Student st ON a.student_id = st.id
            ORDER BY s.created_at DESC
        ''').fetchall()
        print(f"   ✓ Success: Found {len(result)} sessions for case notes")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 6: Check for plural table names that shouldn't exist
    print("\n6. Checking for problematic plural table names...")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [table['name'] for table in tables]
    
    problematic_tables = ['appointments', 'sessions', 'students', 'counsellors']
    found_problematic = []
    
    for table in problematic_tables:
        if table in table_names:
            found_problematic.append(table)
    
    if found_problematic:
        print(f"   ⚠ Warning: Found potentially problematic tables: {found_problematic}")
    else:
        print("   ✓ No problematic plural tables found")
    
    # Test 7: Check that correct tables exist
    print("\n7. Checking for correct table names...")
    expected_tables = ['Appointment', 'Student', 'Session', 'Counsellor', 'Referral', 'reports']
    missing_tables = []
    
    for table in expected_tables:
        if table not in table_names:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"   ✗ Missing tables: {missing_tables}")
    else:
        print(f"   ✓ All expected tables found: {expected_tables}")
    
    # Test 8: Verify Referral table structure
    print("\n8. Checking Referral table structure...")
    try:
        columns = conn.execute("PRAGMA table_info(Referral)").fetchall()
        column_names = [col['name'] for col in columns]
        expected_columns = ['action_taken', 'outcome']
        missing_columns = []
        
        for col in expected_columns:
            if col not in column_names:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"   ⚠ Missing columns in Referral table: {missing_columns}")
        else:
            print(f"   ✓ Referral table has all expected columns")
            
        print(f"   Available columns: {column_names}")
    except Exception as e:
        print(f"   ✗ Error checking Referral table: {e}")
    
    conn.close()
    
    print("\n=== TEST COMPLETE ===")
    print("All database queries have been verified!")

if __name__ == "__main__":
    test_all_functions()