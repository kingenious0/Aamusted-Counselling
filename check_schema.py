import sqlite3

def check_audit_schema():
    try:
        conn = sqlite3.connect('counseling.db')
        cursor = conn.cursor()
        
        # Get columns for audit_logs
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = cursor.fetchall()
        
        print("Columns in audit_logs:")
        for col in columns:
            print(col)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_audit_schema()
