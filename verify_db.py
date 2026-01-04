"""Verify database has Appointment table"""
import sqlite3
import os

db_path = 'counseling.db'
print(f"Checking database at: {os.path.abspath(db_path)}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables in database: {tables}")
    print(f"Has 'Appointment': {'Appointment' in tables}")
    print(f"Has 'appointment' (lowercase): {'appointment' in [t.lower() for t in tables]}")
    
    if 'Appointment' not in tables:
        print("\nFIXING: Appointment table missing, creating it...")
        import db_setup
        db_setup.init_db()
        print("Database reinitialized!")
        
        # Verify again
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables after fix: {tables}")
        print(f"Has 'Appointment' now: {'Appointment' in tables}")
    conn.close()
else:
    print("Database doesn't exist! Creating it...")
    import db_setup
    db_setup.init_db()
    print("Database created!")

