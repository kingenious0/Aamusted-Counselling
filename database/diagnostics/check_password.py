import sqlite3
import os
import sys

# Get database path
try:
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
except:
    base_path = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(base_path, 'counseling.db')
print(f'Database path: {db_path}')

# Check if database exists
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Check app_settings table
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
    if cursor.fetchone():
        print('app_settings table exists')
        
        # Check password hash
        row = conn.execute("SELECT setting_value FROM app_settings WHERE setting_name='password_hash'").fetchone()
        if row:
            print(f'Password hash found: {row["setting_value"][:100]}...')
            print(f'Full hash length: {len(row["setting_value"])} characters')
        else:
            print('No password hash found in app_settings')
            
            # Let's check what's in app_settings
            print("Contents of app_settings:")
            rows = conn.execute("SELECT * FROM app_settings").fetchall()
            for row in rows:
                print(f"  {row['setting_name']}: {row['setting_value']}")
    else:
        print('app_settings table does not exist')
        
        # List all tables
        print("Available tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in cursor.fetchall():
            print(f"  {table['name']}")
    
    conn.close()
else:
    print('Database does not exist')