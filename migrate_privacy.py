"""
GTEC Privacy Migration Script (Multi-DB Safe)
1. Finds ALL .db files in the directory.
2. Cleanses Students and BookingRequests in EACH one that has matching tables.
3. Standardizes initials format.
4. Updates timestamps for sync.
"""
import sqlite3
import os
import sys
from datetime import datetime

sys.path.insert(0, os.getcwd())
try:
    from crypto_utils import encrypt_field, is_encrypted
    from app import name_to_initials
except:
    sys.exit(1)

def cleanse_db(db_path):
    print(f"--- Attempting Cleanse: {db_path} ---")
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if Student table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Student'")
        if not cursor.fetchone():
            print(f"  Skipping {db_path} (No Student table)")
            return

        # 1. Student Table
        students = cursor.execute("SELECT id, name FROM Student").fetchall()
        for s in students:
            base = name_to_initials(s['name'])
            final = f"{base} ({s['id']})"
            
            updates = ["name = ?"]
            params = [final]
            
            # Check for other columns to encrypt
            cursor.execute(f"PRAGMA table_info(Student)")
            cols = [c[1] for c in cursor.fetchall()]
            for f in ['contact', 'email', 'parent_contact']:
                if f in cols:
                    # Fetch value again for this row
                    row = cursor.execute(f"SELECT {f} FROM Student WHERE id=?", (s['id'],)).fetchone()
                    val = row[0]
                    if val and not is_encrypted(val):
                        updates.append(f"{f} = ?")
                        params.append(encrypt_field(val))
            
            if 'updated_at' in cols:
                updates.append("updated_at = ?")
                params.append(now_ts)
            
            params.append(s['id'])
            cursor.execute(f"UPDATE Student SET {', '.join(updates)} WHERE id = ?", params)

        # 2. BookingRequest Table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='BookingRequest'")
        if cursor.fetchone():
            bookings = cursor.execute("SELECT id, full_name FROM BookingRequest").fetchall()
            for bk in bookings:
                new_n = name_to_initials(bk['full_name'])
                updates = ["full_name = ?"]
                params = [new_n]
                cursor.execute(f"PRAGMA table_info(BookingRequest)")
                cols = [c[1] for c in cursor.fetchall()]
                for f in ['phone', 'email']:
                    if f in cols:
                        row = cursor.execute(f"SELECT {f} FROM BookingRequest WHERE id=?", (bk['id'],)).fetchone()
                        val = row[0]
                        if val and not is_encrypted(val):
                            updates.append(f"{f} = ?")
                            params.append(encrypt_field(val))
                if 'updated_at' in cols:
                    updates.append("updated_at = ?")
                    params.append(now_ts)
                params.append(bk['id'])
                cursor.execute(f"UPDATE BookingRequest SET {', '.join(updates)} WHERE id = ?", params)

        # 3. Clinical Tables (Session, CaseManagement, Referral)
        targets = {
            'Session': ['notes', 'outcome'],
            'CaseManagement': ['problems', 'interventions', 'recommendations', 'client_appearance'],
            'Referral': ['reasons']
        }
        for table, fields in targets.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone(): continue
            
            rows = cursor.execute(f"SELECT id FROM {table}").fetchall()
            for r in rows:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                found_fields = [f for f in fields if f in cols]
                if not found_fields: continue
                
                updates = []
                params = []
                cur_row = cursor.execute(f"SELECT {', '.join(found_fields)} FROM {table} WHERE id=?", (r['id'],)).fetchone()
                for i, f in enumerate(found_fields):
                    val = cur_row[i]
                    if val and not is_encrypted(val):
                        updates.append(f"{f} = ?")
                        params.append(encrypt_field(val))
                
                if updates:
                    if 'updated_at' in cols:
                        updates.append("updated_at = ?")
                        params.append(now_ts)
                    params.append(r['id'])
                    cursor.execute(f"UPDATE {table} SET {', '.join(updates)} WHERE id = ?", params)

        conn.commit()
        conn.close()
        print(f"  Successfully Cleansed: {db_path}")
    except Exception as e:
        print(f"  Failed: {db_path} - {e}")

if __name__ == "__main__":
    import glob
    db_files = glob.glob("**/*.db", recursive=True) + glob.glob("*.db")
    # De-duplicate
    db_files = list(set([os.path.abspath(f) for f in db_files]))
    
    for dbf in db_files:
        cleanse_db(dbf)
