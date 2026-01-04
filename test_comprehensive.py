import sqlite3
import os
import sys
from datetime import datetime

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("Testing create_session function with exact Flask route logic...")

try:
    # Test all queries that might be executed in the create_session route
    print("1. Testing appointment query...")
    appointments = conn.execute('''
        SELECT a.id, a.date as date, a.time as time, s.name as student_name
        FROM Appointment a
        JOIN Student s ON a.student_id = s.id
        WHERE a.status = 'scheduled'
        ORDER BY a.date, a.time
    ''').fetchall()
    print(f"   ✓ Appointment query successful! Found {len(appointments)} scheduled appointments")
    
    print("2. Testing if there might be a different query causing the issue...")
    # Let's check if there are any other queries that might reference 'appointments'
    
    # Check for any triggers or views
    triggers = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND sql LIKE '%appointments%'").fetchall()
    if triggers:
        print(f"   Found {len(triggers)} triggers referencing 'appointments':")
        for trigger in triggers:
            print(f"   - {trigger['name']}: {trigger['sql'][:100]}...")
    else:
        print("   ✓ No triggers referencing 'appointments'")
    
    views = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='view' AND sql LIKE '%appointments%'").fetchall()
    if views:
        print(f"   Found {len(views)} views referencing 'appointments':")
        for view in views:
            print(f"   - {view['name']}: {view['sql'][:100]}...")
    else:
        print("   ✓ No views referencing 'appointments'")
    
    print("3. Checking all table names...")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    print("   Tables in database:")
    for table in tables:
        print(f"   - {table['name']}")
        # Check if this table has any foreign keys to 'appointments'
        table_info = conn.execute(f"PRAGMA foreign_key_list({table['name']})").fetchall()
        for fk in table_info:
            if 'appointments' in str(fk):
                print(f"     WARNING: Foreign key referencing 'appointments': {fk}")
    
    print("4. Testing if the error might be in a different function...")
    # Let's test some other common queries that might be called
    
    # Test dashboard queries
    try:
        upcoming_appointments = conn.execute('''
            SELECT a.id, a.date, a.time, s.name as student_name, a.purpose
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            WHERE a.date >= date('now')
            ORDER BY a.date, a.time
            LIMIT 5
        ''').fetchall()
        print(f"   ✓ Dashboard upcoming appointments query successful! Found {len(upcoming_appointments)}")
    except Exception as e:
        print(f"   ✗ Dashboard query failed: {e}")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

conn.close()

print("\nIf the error is still happening, it might be:")
print("1. A different code path being executed")
print("2. A cached version of the code")
print("3. A different database being used")
print("4. The error might be happening in a different function that gets called")