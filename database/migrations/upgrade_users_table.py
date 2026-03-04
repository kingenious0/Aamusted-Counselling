import sqlite3
import os
import sys

def upgrade_db():
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        db_path = os.path.join(base_path, 'counseling.db')
        print(f"Connecting to database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        new_columns = {
            'phone': 'TEXT',
            'email': 'TEXT',
            'profile_pic': 'TEXT'
        }
        
        for col, col_type in new_columns.items():
            if col not in columns:
                print(f"Adding column: {col}")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            else:
                print(f"Column {col} already exists.")
                
        conn.commit()
        conn.close()
        print("Database upgrade completed successfully.")
        
    except Exception as e:
        print(f"Error upgrading database: {e}")

if __name__ == "__main__":
    upgrade_db()
