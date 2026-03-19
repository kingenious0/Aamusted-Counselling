import sqlite3, os, json
db_path = os.path.join(os.getcwd(), 'counseling.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
br = [dict(r) for r in conn.execute("SELECT * FROM BookingRequest WHERE full_name LIKE '%Edem%'").fetchall()]
ap = [dict(r) for r in conn.execute("SELECT * FROM Appointment WHERE student_id IN (SELECT id FROM Student WHERE name LIKE '%Edem%')").fetchall()]
with open('debug_edem.json', 'w') as f:
    json.dump({'bookings': br, 'appointments': ap}, f, indent=2)
conn.close()
