import sqlite3
import os

def add_item_columns_to_outcome_questionnaire():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for i in range(1, 26):
        column_name = f'item{i}'
        try:
            cursor.execute(f"ALTER TABLE OutcomeQuestionnaire ADD COLUMN {column_name} INTEGER")
            print(f"Column '{column_name}' added to OutcomeQuestionnaire table successfully.")
        except sqlite3.OperationalError as e:
            if f"duplicate column name: {column_name}" in str(e):
                print(f"Column '{column_name}' already exists in OutcomeQuestionnaire table.")
            else:
                print(f"Error adding column '{column_name}': {e}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_item_columns_to_outcome_questionnaire()