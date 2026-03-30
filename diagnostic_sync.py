import sqlite3
import os

db_path = r'c:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\counseling.db'

SYNC_TABLES = [
    'Student', 'Appointment', 'session', 'Referral', 
    'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
    'Feedback', 'SessionIssue', 'Notification', 'app_settings',
    'BookingRequest'
]

def check_sync_status():
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    for table in SYNC_TABLES:
        try:
            # Check for records where last_synced_at IS NULL or updated_at > last_synced_at
            query = f"SELECT COUNT(*) FROM {table} WHERE last_synced_at IS NULL"
            unsynced = cursor.execute(query).fetchone()[0]
            
            query2 = f"SELECT COUNT(*) FROM {table} WHERE updated_at > last_synced_at"
            updated = cursor.execute(query2).fetchone()[0]
            
            total = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            
            print(f"Table {table}: {unsynced} new, {updated} updated, {total} total")
        except Exception as e:
            print(f"Table {table}: Error checking: {e}")
            
    conn.close()

if __name__ == "__main__":
    check_sync_status()
