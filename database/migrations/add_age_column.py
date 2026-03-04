import sqlite3
import os

def add_age_column_to_outcome_questionnaire():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE OutcomeQuestionnaire ADD COLUMN age INTEGER")
        print("Column 'age' added to OutcomeQuestionnaire table successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: age" in str(e):
            print("Column 'age' already exists in OutcomeQuestionnaire table.")
        else:
            print(f"Error adding column 'age': {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    add_age_column_to_outcome_questionnaire()