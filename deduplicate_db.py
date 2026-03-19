import sqlite3

db_path = 'counseling.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Find Duplicate Appointments (same student, same date, same time)
# Note: student_id might match cloud ID, so we use it with care
print("--- Local Data Cleanup ---")
cur.execute("""
    DELETE FROM Appointment 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM Appointment 
        GROUP BY student_id, date, time
    )
""")
deleted_appts = cur.rowcount
print(f"Removed {deleted_appts} duplicate appointments.")

# Same for students name/index match
cur.execute("""
    DELETE FROM Student 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM Student 
        GROUP BY name, index_number
    )
""")
deleted_students = cur.rowcount
print(f"Removed {deleted_students} duplicate students.")

conn.commit()
conn.close()
print("Cleanup complete.")
