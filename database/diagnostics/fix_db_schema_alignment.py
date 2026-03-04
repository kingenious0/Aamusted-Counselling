import sqlite3
import os

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Rename counselor_id to Counsellor_id in Appointment table
        cursor.execute("ALTER TABLE Appointment RENAME COLUMN counselor_id TO Counsellor_id")
        print("Renamed counselor_id to Counsellor_id in Appointment table.")
    except Exception as e:
        print(f"Error renaming column in Appointment: {e}")
    
    try:
        # Check if table 'Counsellor' exists (case sensitive check)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Counsellor'")
        if not cursor.fetchone():
            # If it's 'counselor', rename it
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='counselor'")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE counselor RENAME TO Counsellor")
                print("Renamed table counselor to Counsellor.")
    except Exception as e:
        print(f"Error renaming table: {e}")

    conn.commit()
    conn.close()
else:
    print("Database file not found.")
