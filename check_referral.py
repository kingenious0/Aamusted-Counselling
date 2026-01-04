import sqlite3

# Connect to the database
conn = sqlite3.connect('counseling.db')
cursor = conn.cursor()

# Check for referral-related tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%referral%'")
tables = cursor.fetchall()

print("Referral tables found:")
for table in tables:
    print(f"- {table[0]}")

# If we found tables, show their structure
if tables:
    for table_name in [t[0] for t in tables]:
        print(f"\nSchema for {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

conn.close()