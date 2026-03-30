import sqlite3
import uuid

def repair():
    db_path = 'counseling.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    tables = ['Student', 'Appointment', 'session', 'Referral', 'CaseManagement']
    
    for table in tables:
        try:
            # Check if columns exist
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
            
            if 'global_id' not in cols:
                print(f"Skipping {table}: No global_id column")
                continue
                
            # Find records with NULL global_id
            cursor.execute(f"SELECT id FROM {table} WHERE global_id IS NULL")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"Table {table}: All records have global_id")
                continue
                
            print(f"Repairing {len(rows)} records in {table}...")
            
            for row in rows:
                new_gid = str(uuid.uuid4())
                cursor.execute(f"UPDATE {table} SET global_id = ? WHERE id = ?", (new_gid, row['id']))
            
            # Also reset sync for these to ensure they push
            cursor.execute(f"UPDATE {table} SET last_synced_at = NULL WHERE id IN ({','.join(['?']*len(rows))})", [r['id'] for r in rows])
            
            conn.commit()
            print(f"Successfully repaired {table}")
            
        except Exception as e:
            print(f"Error repairing {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    repair()
