"""
Fix database in all possible locations (EXE folder and script folder)
"""
import sqlite3
import os
import sys

def get_possible_db_paths():
    """Get all possible database paths"""
    paths = []
    
    # Current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    paths.append(os.path.join(script_dir, 'counseling.db'))
    
    # EXE distribution folder
    dist_folder = os.path.join(script_dir, 'AAMUSTED_Counseling_System_Distribution')
    if os.path.exists(dist_folder):
        paths.append(os.path.join(dist_folder, 'counseling.db'))
    
    # If running as EXE
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        paths.append(os.path.join(exe_dir, 'counseling.db'))
    
    return paths

def fix_database(db_path):
    """Fix/create database at given path"""
    if not os.path.exists(db_path):
        print(f"Creating database at: {db_path}")
        # Import and run db_setup
        import db_setup
        # Temporarily change to that directory if needed
        orig_dir = os.getcwd()
        try:
            os.chdir(os.path.dirname(db_path))
            db_setup.init_db()
            os.chdir(orig_dir)
        except:
            os.chdir(orig_dir)
            # Try direct creation
            conn = sqlite3.connect(db_path)
            import db_setup
            db_setup.init_db()
    
    # Check and fix table if needed
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if Appointment table exists
    tables = [row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    
    if 'Appointment' not in tables and 'appointment' not in [t.lower() for t in tables]:
        print(f"Creating Appointment table in: {db_path}")
        cursor.execute('''
            CREATE TABLE Appointment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                Counsellor_id INTEGER,
                counselor_id INTEGER,
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
    
    conn.close()
    print(f"✅ Fixed database at: {db_path}")

if __name__ == '__main__':
    print("=" * 60)
    print("Fixing Database in All Locations")
    print("=" * 60)
    
    paths = get_possible_db_paths()
    for path in paths:
        if os.path.exists(os.path.dirname(path)) or path == os.path.join(os.getcwd(), 'counseling.db'):
            try:
                fix_database(path)
            except Exception as e:
                print(f"⚠️  Could not fix {path}: {e}")
    
    print("\n✅ Database fix complete!")
    print("\nNow restart your server!")

