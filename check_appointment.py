import sqlite3

# Connect to the database
conn = sqlite3.connect('counseling.db')
cursor = conn.cursor()

# Check Appointment table columns
cursor.execute('PRAGMA table_info(Appointment)')
columns = cursor.fetchall()
print("Appointment table columns:")
for column in columns:
    print(f"  {column[1]}: {column[2]}")

# Check Appointment table data
cursor.execute('SELECT * FROM Appointment LIMIT 5')
appointment_data = cursor.fetchall()

print("\nAppointment table data (first 5 rows):")
for row in appointment_data:
    print(row)

conn.close()