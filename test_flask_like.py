import sqlite3
import os
from datetime import datetime

# Get the database path exactly as Flask would
def get_db_connection():
    conn = sqlite3.connect('counseling.db')
    conn.row_factory = sqlite3.Row
    return conn

print("Testing Flask-like database connection...")

try:
    # Test the exact same code path as Flask
    conn = get_db_connection()
    
    print("1. Testing the exact query from create_session...")
    appointments = conn.execute('''
        SELECT a.id, a.date as date, a.time as time, s.name as student_name
        FROM Appointment a
        JOIN Student s ON a.student_id = s.id
        WHERE a.status = 'scheduled'
        ORDER BY a.date, a.time
    ''').fetchall()
    
    print(f"   ✓ Query successful! Found {len(appointments)} appointments")
    
    print("2. Testing database file location...")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Database file exists: {os.path.exists('counseling.db')}")
    if os.path.exists('counseling.db'):
        print(f"   Database file size: {os.path.getsize('counseling.db')} bytes")
    
    print("3. Testing if there might be a different database file...")
    # Check if there are multiple database files
    for file in os.listdir('.'):
        if file.endswith('.db'):
            print(f"   Found database file: {file}")
    
    print("4. Testing connection to a different database...")
    # Maybe Flask is using a different connection
    conn2 = sqlite3.connect('counseling.db')
    try:
        result = conn2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'").fetchone()
        if result:
            print("   ✗ Found 'appointments' table (plural)!")
        else:
            print("   ✓ No 'appointments' table found")
    except:
        print("   ✓ No 'appointments' table found")
    finally:
        conn2.close()
    
    conn.close()
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting complete.")