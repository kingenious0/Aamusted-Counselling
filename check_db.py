import sqlite3
import os

db_path = r'c:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\counseling.db'

def check_schema():
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Student Table Schema ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Student'")
    schema = cursor.fetchone()
    if schema:
        print(schema[0])
    
    conn.close()

if __name__ == "__main__":
    check_schema()
