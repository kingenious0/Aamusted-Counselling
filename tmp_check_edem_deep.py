import sqlite3, os, json
db_path = os.path.join(os.getcwd(), 'counseling.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM BookingRequest WHERE full_name LIKE '%Edem%'").fetchall()
for r in rows:
    print(dict(r))
print("-" * 20)
rows = conn.execute("SELECT * FROM Appointment WHERE student_id IN (SELECT id FROM Student WHERE name LIKE '%Edem%')").fetchall()
for r in rows:
    print(dict(r))
conn.close()
