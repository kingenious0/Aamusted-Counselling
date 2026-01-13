import sqlite3

def check_case_mgmt_schema():
    try:
        conn = sqlite3.connect('counseling.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(CaseManagement)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_case_mgmt_schema()
