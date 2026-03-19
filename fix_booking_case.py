import sqlite3

db_path = 'counseling.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Update the status case to match what app.py expects ('Pending' with capital P)
cur.execute("UPDATE BookingRequest SET status = 'Pending' WHERE status = 'pending'")
count = cur.rowcount

conn.commit()
conn.close()

print(f"Standardized {count} booking statuses to 'Pending'.")
