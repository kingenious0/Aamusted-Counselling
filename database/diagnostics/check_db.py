import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check specifically for Appointment or appointments tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Appointment' OR name='appointments');")
appointment_tables = cursor.fetchall()

print("Appointment tables found:")
for table in appointment_tables:
    print(f"- {table[0]}")

if not appointment_tables:
    print("No Appointment or appointments tables found!")
    
    # Let's check what tables we do have
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = cursor.fetchall()
    print("\nAll tables in database:")
    for table in all_tables:
        print(f"- {table[0]}")
else:
    # Show schema for appointment table(s)
    for table in appointment_tables:
        table_name = table[0]
        print(f"\nSchema for table '{table_name}':")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

conn.close()