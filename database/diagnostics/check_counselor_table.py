import sqlite3

# Connect to the database
conn = sqlite3.connect('counseling.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(f"  {table[0]}")

# Check if Counselor or Counsellor exists
counselor_tables = [table[0] for table in tables if 'counselor' in table[0].lower()]
print(f"\nCounselor-related tables: {counselor_tables}")

conn.close()