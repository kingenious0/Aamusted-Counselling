import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize database - works in both dev and EXE mode"""
    # Determine correct database path (same logic as app.py)
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE - database in EXE folder
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script - database in script folder
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(base_path, 'counseling.db')
    print(f"[DB_SETUP] Initializing database at: {db_path}")
    
    # Connect to SQLite database (creates it if it doesn't exist)
    # Use timeout to prevent locking issues
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")

    # Check if SessionIssue table exists and has issue_name column
    cursor.execute("PRAGMA table_info(SessionIssue)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'issue_name' not in columns:
        # If issue_name column does not exist, it means the old schema is present.
        # We need to drop the old SessionIssue table and create the new one.
        # This will unfortunately delete existing SessionIssue data.
        cursor.execute("DROP TABLE IF EXISTS SessionIssue")
        print("Dropped old SessionIssue table.")

    # Create tables
    cursor.executescript('''
        -- Student table
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

        -- Counsellor table
        CREATE TABLE IF NOT EXISTS Counsellor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Appointment table
        CREATE TABLE IF NOT EXISTS Appointment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            Counsellor_id INTEGER,
            date DATE NOT NULL,
            time TIME NOT NULL,
            purpose TEXT,
            status TEXT DEFAULT 'Scheduled', -- Standardized default
            urgency TEXT,                   -- New: Crisis, Urgent, Normal
            checked_in_at TIMESTAMP,        -- New: Workflow timestamp
            sent_to_counsellor_at TIMESTAMP,-- New: Workflow timestamp
            accepted_at TIMESTAMP,          -- New: Workflow timestamp
            completed_at TIMESTAMP,         -- New: Workflow timestamp
            referral_reason TEXT,           -- New: Context for handover
            referral_source TEXT,           -- New: Reporting
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(id),
            FOREIGN KEY (Counsellor_id) REFERENCES Counsellor(id)
        );

        -- reports table
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            report_type TEXT,
            file_path TEXT,
            summary TEXT
        );

        -- session table
        CREATE TABLE IF NOT EXISTS session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            session_type TEXT,
            notes TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appointment_id) REFERENCES Appointment(id)
        );

        -- CaseManagement table
        CREATE TABLE IF NOT EXISTS CaseManagement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            client_appearance TEXT,
            problems TEXT,
            interventions TEXT,
            recommendations TEXT,
            next_visit_date DATE,
            counsellor_signature TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES session(id)
        );

        -- Referral table
        CREATE TABLE IF NOT EXISTS Referral (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            referred_by TEXT,
            contact TEXT,
            reasons TEXT,
            action_taken TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES session(id)
        );

        -- OutcomeQuestionnaire table
        CREATE TABLE IF NOT EXISTS OutcomeQuestionnaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            session_id INTEGER,
            age INTEGER,
            sex TEXT,

            item1 INTEGER, item2 INTEGER, item3 INTEGER, item4 INTEGER, item5 INTEGER,
            item6 INTEGER, item7 INTEGER, item8 INTEGER, item9 INTEGER, item10 INTEGER,
            item11 INTEGER, item12 INTEGER, item13 INTEGER, item14 INTEGER, item15 INTEGER,
            item16 INTEGER, item17 INTEGER, item18 INTEGER, item19 INTEGER, item20 INTEGER,
            item21 INTEGER, item22 INTEGER, item23 INTEGER, item24 INTEGER, item25 INTEGER,
            total_score INTEGER,
            completion_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(id),
            FOREIGN KEY (session_id) REFERENCES session(id)
        );

        -- DASS21 table
        CREATE TABLE IF NOT EXISTS DASS21 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            depression_score FLOAT,
            anxiety_score FLOAT,
            stress_score FLOAT,
            completion_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(id)
        );

        -- SessionIssue table
        CREATE TABLE IF NOT EXISTS SessionIssue (
            session_id INTEGER,
            issue_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (session_id, issue_name),
            FOREIGN KEY (session_id) REFERENCES session(id)
        );

        -- Feedback table
        CREATE TABLE IF NOT EXISTS Feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            rating INTEGER,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES session(id)
        );

        -- Users table for RBAC
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT NOT NULL, -- 'Secretary', 'Counsellor', 'Admin'
            last_login TIMESTAMP,
            phone TEXT,
            email TEXT,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Audit Logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- App Settings table for session configuration
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT NOT NULL UNIQUE,
            setting_value TEXT
        );

        -- Notification table (NEW)
        CREATE TABLE IF NOT EXISTS Notification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            type TEXT NOT NULL, -- 'in_app', 'sms', 'system'
            link TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- SMS Queue table (NEW)
        CREATE TABLE IF NOT EXISTS SMSQueue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_number TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending', -- pending, sent, failed
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP
        );
    ''')

    # Check if 'outcome' column exists in 'session' table, if not, add it
    # Add outcome column to session table if it doesn't exist
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # helper to add column if missing
    def add_column_if_missing(table, column, col_type):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [info[1] for info in cursor.fetchall()]
        if column not in cols:
            print(f"[DB_SETUP] Adding missing column {column} to {table}")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")

    # Session table updates
    add_column_if_missing('session', 'outcome', 'TEXT')

    # Appointment table updates for Workflow
    add_column_if_missing('Appointment', 'urgency', 'TEXT')
    add_column_if_missing('Appointment', 'checked_in_at', 'TIMESTAMP')
    add_column_if_missing('Appointment', 'sent_to_counsellor_at', 'TIMESTAMP')
    add_column_if_missing('Appointment', 'accepted_at', 'TIMESTAMP')
    add_column_if_missing('Appointment', 'completed_at', 'TIMESTAMP')
    add_column_if_missing('Appointment', 'referral_reason', 'TEXT')
    add_column_if_missing('Appointment', 'referral_source', 'TEXT')

    # Users table updates
    add_column_if_missing('users', 'phone', 'TEXT')
    add_column_if_missing('users', 'email', 'TEXT')
    add_column_if_missing('users', 'profile_pic', 'TEXT')

    # App Settings sync updates
    add_column_if_missing('app_settings', 'updated_at', 'TIMESTAMP')
    # Manual backfill since ADD COLUMN DEFAULT CURRENT_TIMESTAMP can be flaky in some SQLite versions
    try:
        cursor.execute("UPDATE app_settings SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
    except:
        pass
    add_column_if_missing('app_settings', 'global_id', 'TEXT')
    # Uniqueness enforced by logic/UUID

    # Backfill global_id for app_settings if missing
    try:
        settings_rows = cursor.execute("SELECT id FROM app_settings WHERE global_id IS NULL").fetchall()
        if settings_rows:
            import uuid
            print(f"[DB_SETUP] Backfilling global_id for {len(settings_rows)} settings...")
            for row in settings_rows:
                row_id = row[0]
                new_uuid = str(uuid.uuid4())
                cursor.execute("UPDATE app_settings SET global_id = ? WHERE id = ?", (new_uuid, row_id))
    except Exception as e:
        print(f"[DB_SETUP] Warning during backfill: {e}")

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Insert predefined counsellors - Only Mrs. Gertrude Effeh Brew
    cursor.executescript('''
        DELETE FROM Counsellor;
        INSERT OR IGNORE INTO Counsellor (id, name, contact) VALUES
            (1, 'Mrs. Gertrude Effeh Brew', '');
    ''')




    # Insert default users if not already present
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ('admin', generate_password_hash("Admin123"), 'System Administrator', 'Admin'),
            ('secretary', generate_password_hash("Secretary123"), 'Front Desk Office', 'Secretary'),
            ('counsellor', generate_password_hash("Counsellor123"), 'Mrs. Gertrude Effeh Brew', 'Counsellor')
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            users
        )
        print("[DB_SETUP] Default users created.")

    # Insert default password hash in app_settings (legacy support)
    cursor.execute("SELECT COUNT(*) FROM app_settings WHERE setting_name = 'password_hash'")
    if cursor.fetchone()[0] == 0:
        default_password_hash = generate_password_hash("Counsellor123")
        cursor.execute("INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)",
                       ("password_hash", default_password_hash))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized successfully!')