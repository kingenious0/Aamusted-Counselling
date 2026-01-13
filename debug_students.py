import sqlite3
import os

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    with open('students_debug_full.txt', 'w') as f:
        f.write("Students in DB:\n")
        for s in students:
            f.write(str(dict(s)) + "\n")
            
    conn.close()
else:
    print("Database file not found.")
