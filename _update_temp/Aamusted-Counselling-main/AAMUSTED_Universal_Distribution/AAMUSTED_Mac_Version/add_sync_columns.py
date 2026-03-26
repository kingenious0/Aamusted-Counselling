import sqlite3
import uuid
from datetime import datetime
import os
import sys

# DATABASE_PATH = 'counseling.db'

def get_db_path():
    """Get database path - works in both dev and EXE mode"""
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'counseling.db')

def add_column_safe(cursor, table, column_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        print(f"Added column to {table}: {column_def}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column already exists in {table}: {column_def.split()[0]}")
        else:
            print(f"Error adding column to {table}: {e}")

def migrate():
    db_path = get_db_path()
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Tables that need sync capabilities
    sync_tables = [
        'Student', 
        'Appointment', 
        'session', 
        'Referral', 
        'CaseManagement', 
        'OutcomeQuestionnaire', 
        'DASS21', 
        'Feedback',
        'SessionIssue',
        'Notification' # Maybe sync notifications? Use case dependent, but safe to allow.
    ]

    print("--- Adding Sync Columns ---")
    for table in sync_tables:
        print(f"Processing {table}...")
        # SQLite cannot add UNIQUE column in ALTER TABLE. 
        # Strategy: Add column as TEXT, then create UNIQUE INDEX.
        add_column_safe(cursor, table, "global_id TEXT")
        
        # Create unique index for global_id
        try:
            index_name = f"idx_{table}_global_id"
            cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON {table}(global_id)")
            print(f"Created unique index {index_name}")
        except Exception as e:
            print(f"Error creating index on {table}: {e}")

        add_column_safe(cursor, table, "updated_at TIMESTAMP")
        add_column_safe(cursor, table, "last_modified_by TEXT") # e.g., 'SECRETARY_PC'
        add_column_safe(cursor, table, "is_deleted BOOLEAN DEFAULT 0")
        add_column_safe(cursor, table, "sync_status TEXT DEFAULT 'pending'") # pending, synced

    conn.commit()
    
    print("\n--- Backfilling UUIDs for existing records ---")
    # Generate UUIDs for rows that don't have them
    for table in sync_tables:
        try:
            # Check if there are any rows with NULL global_id
            # Note: We need to handle potential errors if the previous run partly succeeded or failed
            rows_to_update = cursor.execute(f"SELECT rowid FROM {table} WHERE global_id IS NULL").fetchall()
            
            if rows_to_update:
                print(f"Backfilling {len(rows_to_update)} rows in {table}...")
                count = 0
                for row in rows_to_update:
                    new_uuid = str(uuid.uuid4())
                    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(f"UPDATE {table} SET global_id = ?, updated_at = ? WHERE rowid = ?", (new_uuid, now, row[0]))
                    count += 1
                print(f"  - Updated {count} records in {table}")
            else:
                print(f"  - No backfill needed for {table}")
                
        except Exception as e:
            print(f"Error backfilling {table}: {e}")

    conn.commit()
    conn.close()
    print("\nMigration completed successfully.")

if __name__ == "__main__":
    migrate()
