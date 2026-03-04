import sqlite3
import os
import sys

def fix_db():
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))

    db_path = os.path.join(base_path, 'counseling.db')
    print(f"Fixing database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check/Add global_id to app_settings
    try:
        cursor.execute("SELECT global_id FROM app_settings LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding global_id column...")
        cursor.execute("ALTER TABLE app_settings ADD COLUMN global_id TEXT")
    
    # 2. Check/Add updated_at to app_settings
    try:
        cursor.execute("SELECT updated_at FROM app_settings LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding updated_at column...")
        cursor.execute("ALTER TABLE app_settings ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # 3. Backfill global_id
    import uuid
    rows = cursor.execute("SELECT id FROM app_settings WHERE global_id IS NULL").fetchall()
    print(f"Backfilling {len(rows)} global_ids...")
    for row in rows:
        cursor.execute("UPDATE app_settings SET global_id = ? WHERE id = ?", (str(uuid.uuid4()), row[0]))

    conn.commit()
    conn.close()
    print("Database fix complete.")

if __name__ == "__main__":
    fix_db()
