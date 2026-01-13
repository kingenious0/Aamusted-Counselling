import sqlite3

def check_schema():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()
    
    # Check Appointment table
    print("--- Appointment Table ---")
    cursor.execute("PRAGMA table_info(Appointment)")
    for col in cursor.fetchall():
        print(col)
        
    # Check intake_forms table
    print("\n--- intake_forms Table ---")
    cursor.execute("PRAGMA table_info(intake_forms)")
    for col in cursor.fetchall():
        print(col)

    conn.close()

if __name__ == "__main__":
    check_schema()
