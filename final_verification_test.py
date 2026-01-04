import sqlite3
import os

def test_all_fixed_queries():
    """Test all the queries that were fixed to ensure they work correctly"""
    
    db_path = 'counseling.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    print("Testing all fixed database queries...")
    
    # Test 1: create_session function query
    print("\n1. Testing create_session query...")
    try:
        appointments = conn.execute('''
            SELECT a.id, a.date as date, a.time as time, s.name as student_name
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            WHERE a.status = 'scheduled'
            ORDER BY a.date, a.time
        ''').fetchall()
        print(f"   ✓ Success! Found {len(appointments)} scheduled appointments")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2: dashboard function queries
    print("\n2. Testing dashboard queries...")
    try:
        # Upcoming appointments
        upcoming = conn.execute('''
            SELECT a.id, a.date, a.time, s.name as student_name, a.purpose
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            WHERE a.date >= date('now')
            ORDER BY a.date, a.time
            LIMIT 5
        ''').fetchall()
        print(f"   ✓ Upcoming appointments: {len(upcoming)}")
        
        # Recent sessions
        sessions = conn.execute('''
            SELECT s.id, s.created_at, st.name as student_name, a.purpose
            FROM Session s
            JOIN Appointment a ON s.appointment_id = a.id
            JOIN Student st ON a.student_id = st.id
            ORDER BY s.created_at DESC
            LIMIT 5
        ''').fetchall()
        print(f"   ✓ Recent sessions: {len(sessions)}")
        
        # Recent referrals
        referrals = conn.execute('''
            SELECT r.*, s.name as student_name
            FROM Referral r
            JOIN Session sess ON r.session_id = sess.id
            JOIN Appointment a ON sess.appointment_id = a.id
            JOIN Student s ON a.student_id = s.id
            ORDER BY r.created_at DESC
            LIMIT 5
        ''').fetchall()
        print(f"   ✓ Recent referrals: {len(referrals)}")
        
    except Exception as e:
        print(f"   ✗ Dashboard queries failed: {e}")
    
    # Test 3: Other function queries
    print("\n3. Testing other function queries...")
    
    # Students function
    try:
        students = conn.execute('''
            SELECT s.*, 
                   COUNT(DISTINCT sess.id) as session_count
            FROM Student s
            LEFT JOIN Session sess ON s.id = sess.student_id
            GROUP BY s.id
            ORDER BY s.name
        ''').fetchall()
        print(f"   ✓ Students query: {len(students)} students")
    except Exception as e:
        print(f"   ✗ Students query failed: {e}")
    
    # Referral function
    try:
        sessions = conn.execute('''
            SELECT s.id, s.created_at, st.name as student_name, st.id as student_id, 'Counsellor' as Counsellor_name
            FROM Session s
            JOIN Student st ON s.student_id = st.id
            ORDER BY s.created_at DESC
        ''').fetchall()
        print(f"   ✓ Referral sessions query: {len(sessions)} sessions")
    except Exception as e:
        print(f"   ✗ Referral query failed: {e}")
    
    # All referrals function
    try:
        all_referrals = conn.execute('''
            SELECT r.*, s.name as student_name, s.email as student_contact
            FROM Referral r
            JOIN Session sess ON r.session_id = sess.id
            JOIN Student s ON sess.student_id = s.id
            ORDER BY r.created_at DESC
        ''').fetchall()
        print(f"   ✓ All referrals query: {len(all_referrals)} referrals")
    except Exception as e:
        print(f"   ✗ All referrals query failed: {e}")
    
    # Test 4: Check for any remaining plural table references
    print("\n4. Checking for any remaining plural table references...")
    
    # Check for any remaining 'appointments' references
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='appointments'")
    if cursor.fetchone():
        print("   ⚠️  Found 'appointments' table (plural) - this might cause issues")
    else:
        print("   ✓ No 'appointments' table found")
    
    # Check for any remaining 'sessions' references
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='sessions'")
    if cursor.fetchone():
        print("   ⚠️  Found 'sessions' table (plural) - this might cause issues")
    else:
        print("   ✓ No 'sessions' table found")
    
    # Check for any remaining 'reports' references
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='reports'")
    if cursor.fetchone():
        print("   ✓ Found 'reports' table (this one is correct)")
    else:
        print("   ? No 'reports' table found")
    
    conn.close()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_all_fixed_queries()