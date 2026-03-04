import sqlite3

def create_intake_table():
    try:
        conn = sqlite3.connect('counseling.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='intake_forms';")
        if cursor.fetchone():
            print("Table 'intake_forms' already exists.")
        else:
            print("Creating table 'intake_forms'...")
            cursor.execute('''
                CREATE TABLE intake_forms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    date TEXT,
                    presenting_issue TEXT,
                    background TEXT,
                    mental_status TEXT,
                    risk_assessment TEXT,
                    diagnosis TEXT,
                    treatment_plan TEXT,
                    counselor_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES Student (id),
                    FOREIGN KEY (counselor_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
            print("Table created successfully.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_intake_table()
