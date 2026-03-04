import sqlite3
import os
from datetime import datetime

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("Testing create_session function logic...")

try:
    # Test the exact query from line 237
    print("Executing query from create_session function...")
    appointments = conn.execute('''
        SELECT a.id, a.date as date, a.time as time, s.name as student_name
        FROM Appointment a
        JOIN Student s ON a.student_id = s.id
        WHERE a.status = 'scheduled'
        ORDER BY a.date, a.time
    ''').fetchall()
    
    print(f"Query successful! Found {len(appointments)} appointments with status 'scheduled'")
    
    # Show all appointments regardless of status
    all_appointments = conn.execute('''
        SELECT a.id, a.date, a.time, a.status, s.name as student_name
        FROM Appointment a
        JOIN Student s ON a.student_id = s.id
        ORDER BY a.date, a.time
    ''').fetchall()
    
    print(f"\nAll appointments (regardless of status): {len(all_appointments)}")
    for appt in all_appointments:
        print(f"  ID: {appt['id']}, Date: {appt['date']}, Time: {appt['time']}, Status: {appt['status']}, Student: {appt['student_name']}")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

conn.close()