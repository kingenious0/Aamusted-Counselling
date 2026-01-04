import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test the exact query from line 237
try:
    print("Testing the query from line 237...")
    result = cursor.execute('''
        SELECT a.id, a.date as date, a.time as time, s.name as student_name
        FROM Appointment a
        JOIN Student s ON a.student_id = s.id
        WHERE a.status = 'scheduled'
        ORDER BY a.date, a.time
    ''').fetchall()
    
    print(f"Query successful! Found {len(result)} results:")
    for row in result[:5]:  # Show first 5 results
        print(f"  ID: {row[0]}, Date: {row[1]}, Time: {row[2]}, Student: {row[3]}")
        
except Exception as e:
    print(f"Query failed with error: {e}")

# Check if there are any records in Appointment table
cursor.execute("SELECT COUNT(*) FROM Appointment")
count = cursor.fetchone()[0]
print(f"\nTotal records in Appointment table: {count}")

# Check if there are any records in Student table
cursor.execute("SELECT COUNT(*) FROM Student")
count = cursor.fetchone()[0]
print(f"Total records in Student table: {count}")

conn.close()