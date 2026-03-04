import sqlite3
import os

db_path = 'counseling.db'

def check_schema():
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Check Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    if 'Notification' in tables:
        print("✅ Notification table exists")
    else:
        print("❌ Notification table MISSING")

    if 'SMSQueue' in tables:
        print("✅ SMSQueue table exists")
    else:
        print("❌ SMSQueue table MISSING")

    print("\n--- Check Appointment Columns ---")
    cursor.execute("PRAGMA table_info(Appointment)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {columns}")
    
    required_cols = ['urgency', 'checked_in_at', 'sent_to_counsellor_at', 'accepted_at', 'completed_at', 'referral_reason']
    for col in required_cols:
        if col in columns:
            print(f"✅ Column '{col}' exists")
        else:
            print(f"❌ Column '{col}' MISSING")

    conn.close()

if __name__ == "__main__":
    check_schema()
