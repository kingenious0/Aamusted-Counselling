import sqlite3

db_path = 'counseling.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Update the new booking to 'pending' so it shows on the dashboard intake list
ref = 'BR-9SNHB98D'
cur.execute("UPDATE BookingRequest SET status = 'pending' WHERE reference = ?", (ref,))
count = cur.rowcount

conn.commit()
conn.close()

if count > 0:
    print(f"Success: Record {ref} updated to pending.")
else:
    print(f"Record {ref} not found in local database yet.")
