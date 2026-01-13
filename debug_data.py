import sqlite3
import os
from datetime import datetime

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"System Date: {datetime.now().date().isoformat()}")
    
    cursor.execute("SELECT * FROM Appointment")
    rows = cursor.fetchall()
    print("\nAppointments in DB:")
    for row in rows:
        print(dict(row))
        
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("\nUsers in DB:")
    for user in users:
        print({k: user[k] for k in user.keys() if k != 'password_hash'})
        
    conn.close()
else:
    print("Database file not found.")
