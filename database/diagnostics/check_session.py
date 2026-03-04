import sqlite3

# Connect to the database
conn = sqlite3.connect('counseling.db')
cursor = conn.cursor()

# Check Session table data
cursor.execute('SELECT * FROM Session LIMIT 5')
session_data = cursor.fetchall()

print("Session table data (first 5 rows):")
for row in session_data:
    print(row)

# Check if there's an appointments table (case insensitive)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name) LIKE '%appoint%'")
appointment_tables = cursor.fetchall()
print("\nTables with 'appoint' in name:")
for table in appointment_tables:
    print(f"- {table[0]}")

# Check Session table columns
cursor.execute('PRAGMA table_info(Session)')
columns = cursor.fetchall()
print("\nSession table columns:")
for column in columns:
    print(f"  {column[1]}: {column[2]}")

conn.close()