import sqlite3, os
db_path = os.path.join(os.getcwd(), 'counseling.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT s.name, a.date, a.time, a.status FROM Appointment a JOIN Student s ON a.student_id = s.id WHERE s.name LIKE '%Edem%'").fetchall()
for r in rows:
    print(f"Name: {r['name']}, Date: {r['date']}, Time: {r['time']}, Status: {r['status']}")
conn.close()
