import sqlite3

def migrate_statuses():
    try:
        conn = sqlite3.connect('counseling.db')
        cursor = conn.cursor()
        
        mapping = {
            'scheduled': 'Scheduled',
            'sent_to_counsellor': 'Sent to Counsellor',
            'in_session': 'In Session',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        
        for old, new in mapping.items():
            cursor.execute("UPDATE Appointment SET status = ? WHERE status = ?", (new, old))
            print(f"Migrated {cursor.rowcount} records from '{old}' to '{new}'")
            
        conn.commit()
        conn.close()
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_statuses()
