import sqlite3

def create_appointments_table():
    # Connect to the database
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()
    
    # Create the appointments table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        purpose TEXT,
        status TEXT DEFAULT 'scheduled',
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Appointments table created successfully!")

if __name__ == "__main__":
    create_appointments_table()