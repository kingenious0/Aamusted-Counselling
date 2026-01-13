import sqlite3
import os

db_path = 'counseling.db'
with open('db_columns.txt', 'w') as f:
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Appointment)")
        columns = cursor.fetchall()
        f.write("Columns in Appointment table:\n")
        for col in columns:
            f.write(str(col) + "\n")
        conn.close()
    else:
        f.write("Database file not found.\n")
