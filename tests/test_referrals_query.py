import sqlite3

# Test the referrals query to make sure it works
try:
    conn = sqlite3.connect('counseling.db')
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    # Test the exact query from the dashboard function
    referrals = conn.execute('''
        SELECT r.id, r.referred_by, r.reasons, r.created_at,
               s.name as student_name
        FROM Referral r
        JOIN Session sess ON r.session_id = sess.id
        JOIN Appointment a ON sess.appointment_id = a.id
        JOIN Student s ON a.student_id = s.id
        ORDER BY r.created_at DESC
        LIMIT 5
    ''').fetchall()
    
    print(f"Query successful! Found {len(referrals)} referrals")
    if referrals:
        print("First referral:")
        print(f"  ID: {referrals[0]['id']}")
        print(f"  Referred by: {referrals[0]['referred_by']}")
        print(f"  Student: {referrals[0]['student_name']}")
        print(f"  Reasons: {referrals[0]['reasons']}")
    else:
        print("No referrals found in database")
        
    conn.close()
    
except sqlite3.OperationalError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Other error: {e}")