import sqlite3
import os

def check_table_schema(table_name):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Schema for {table_name} table:")
        for col in columns:
            print(col)
    except sqlite3.OperationalError as e:
        print(f"Error checking schema for {table_name}: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_table_schema('Session')
    check_table_schema('OutcomeQuestionnaire')