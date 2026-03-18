import urllib.request
import sqlite3

# Test booking portal route
try:
    res = urllib.request.urlopen('http://127.0.0.1:5000/booking')
    print('GET /booking:', res.status)
except Exception as e:
    print('GET /booking ERROR:', e)

# Confirm DB state
conn = sqlite3.connect('counseling.db')
conn.row_factory = sqlite3.Row
students = conn.execute('SELECT id, name, case_number FROM Student').fetchall()
print('Students:')
for s in students:
    print(' ', s['id'], s['name'], '->', s['case_number'])

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'").fetchall()
has_booking = any(t['name'] == 'BookingRequest' for t in tables)
print('BookingRequest exists:', has_booking)
conn.close()
