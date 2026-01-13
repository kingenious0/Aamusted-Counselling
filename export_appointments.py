import sqlite3
import os

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, student_id, date, status FROM Appointment")
    rows = cursor.fetchall()
    with open('appointments_debug.txt', 'w') as f:
        f.write("Appointments in DB:\n")
        for row in rows:
            f.write(str(dict(row)) + "\n")
            
    conn.close()
    print("Exported appointment data to appointments_debug.txt")
else:
    print("Database file not found.")
