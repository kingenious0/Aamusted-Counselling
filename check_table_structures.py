import sqlite3

# Connect to the database
conn = sqlite3.connect('counseling.db')
conn.row_factory = sqlite3.Row

print("Checking Session table structure...")

# Get the schema for Session table
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Session)")
session_columns = cursor.fetchall()

print("Session table columns:")
for col in session_columns:
    print(f"  {col['cid']}: {col['name']} ({col['type']}) - {col['dflt_value']} {col['pk']}")

print("\nChecking Student table structure...")
cursor.execute("PRAGMA table_info(Student)")
student_columns = cursor.fetchall()

print("Student table columns:")
for col in student_columns:
    print(f"  {col['cid']}: {col['name']} ({col['type']}) - {col['dflt_value']} {col['pk']}")

print("\nChecking Referral table structure...")
cursor.execute("PRAGMA table_info(Referral)")
referral_columns = cursor.fetchall()

print("Referral table columns:")
for col in referral_columns:
    print(f"  {col['cid']}: {col['name']} ({col['type']}) - {col['dflt_value']} {col['pk']}")

conn.close()