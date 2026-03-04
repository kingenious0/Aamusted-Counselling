import sqlite3

def add_signature_column():
    try:
        conn = sqlite3.connect('counseling.db')
        cursor = conn.cursor()
        
        # Check if column exists first to avoid error
        cursor.execute("PRAGMA table_info(CaseManagement)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'counsellor_signature' not in columns:
            print("Adding 'counsellor_signature' column to CaseManagement...")
            cursor.execute("ALTER TABLE CaseManagement ADD COLUMN counsellor_signature TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column 'counsellor_signature' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_signature_column()
