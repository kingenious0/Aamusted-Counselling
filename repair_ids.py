
import sqlite3
import uuid

def repair_ids():
    conn = sqlite3.connect('counseling.db')
    cur = conn.cursor()
    
    # These were misidentified as global_ids
    invalid_ids = ['MS-2026-0001', 'OE-2026-0001', 'IK-2026-0001']
    
    for old_id in invalid_ids:
        new_uuid = str(uuid.uuid4())
        # Also set updated_at to force a push
        cur.execute("""
            UPDATE Student 
            SET global_id = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE global_id = ?
        """, (new_uuid, old_id))
        print(f"Repaired {old_id} -> {new_uuid}")
        
    conn.commit()
    print("All Student IDs repaired successfully.")
    conn.close()

if __name__ == '__main__':
    repair_ids()
