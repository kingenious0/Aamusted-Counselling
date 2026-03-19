import sqlite3
import os

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    tables = [
        'Student', 'Appointment', 'session', 'Referral', 
        'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
        'Feedback', 'SessionIssue', 'Notification', 'app_settings',
        'BookingRequest'
    ]
    
    for table in tables:
        try:
            # Check existing columns
            cur.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cur.fetchall()]
            
            # Add missing columns
            if 'global_id' not in cols and table not in ['app_settings', 'BookingRequest']:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN global_id TEXT")
                print(f"Added global_id to {table}")
                
            if 'updated_at' not in cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                print(f"Added updated_at to {table}")
                
            if 'last_synced_at' not in cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN last_synced_at DATETIME")
                print(f"Added last_synced_at to {table}")
                
            if 'is_deleted' not in cols:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
                print(f"Added is_deleted to {table}")
                
        except Exception as e:
            print(f"Error updating table {table}: {e}")
            
    conn.commit()
    conn.close()
    print("Local database schema alignment completed.")
else:
    print("Database not found.")
