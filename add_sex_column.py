import sqlite3

def add_sex_column():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE OutcomeQuestionnaire ADD COLUMN sex TEXT")
        print("Column 'sex' added to OutcomeQuestionnaire table successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'sex' already exists in OutcomeQuestionnaire table.")
        else:
            print(f"Error adding column 'sex': {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    add_sex_column()