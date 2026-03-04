"""
Check and fix database issues - ensure all tables exist with correct names
"""
import sqlite3
import os

def check_and_fix_database():
    """Check database and create missing tables"""
    db_path = 'counseling.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found! Creating it...")
        # Run db_setup to create database
        import db_setup
        db_setup.init_db()
        print("Database created successfully!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all existing tables
    existing_tables = [row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    
    print(f"\nExisting tables in database: {existing_tables}")
    
    # Check if Appointment table exists (check both cases)
    appointment_exists = any(
        table.lower() == 'appointment' 
        for table in existing_tables
    )
    
    if not appointment_exists:
        print("\n⚠️  Appointment table not found! Creating it...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Appointment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                counselor_id INTEGER,
                Counsellor_id INTEGER,
                date DATE NOT NULL,
                time TIME NOT NULL,
                purpose TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES Student(id),
                FOREIGN KEY (Counsellor_id) REFERENCES Counsellor(id)
            );
        ''')
        conn.commit()
        print("✅ Appointment table created!")
    else:
        print("✅ Appointment table exists")
    
    # Check Student table
    student_exists = any(
        table.lower() == 'student' 
        for table in existing_tables
    )
    
    if not student_exists:
        print("\n⚠️  Student table not found! Creating it...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                contact TEXT,
                index_number TEXT NOT NULL,
                department TEXT NOT NULL,
                faculty TEXT,
                programme TEXT NOT NULL,
                parent_contact TEXT,
                hall_of_residence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        print("✅ Student table created!")
    else:
        print("✅ Student table exists")
    
    # Check Counsellor table
    counsellor_exists = any(
        table.lower() in ['counsellor', 'counselor']
        for table in existing_tables
    )
    
    if not counsellor_exists:
        print("\n⚠️  Counsellor table not found! Creating it...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Counsellor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Insert Mrs. Gertrude Effeh Brew
        cursor.execute('''
            INSERT OR IGNORE INTO Counsellor (id, name, contact)
            VALUES (1, 'Mrs. Gertrude Effeh Brew', '')
        ''')
        conn.commit()
        print("✅ Counsellor table created with Mrs. Gertrude Effeh Brew!")
    else:
        print("✅ Counsellor table exists")
    
    conn.close()
    print("\n✅ Database check complete!")

if __name__ == '__main__':
    print("=" * 60)
    print("Database Check and Fix Utility")
    print("=" * 60)
    check_and_fix_database()

