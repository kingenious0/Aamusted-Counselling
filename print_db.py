import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('counseling.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        user_full_name = 'Mrs. Gertrude Effeh Brew'
        username = 'counsellor'
        
        counsellor = conn.execute(
            "SELECT id FROM Counsellor WHERE name = ? OR name = ?",
            (user_full_name, username)).fetchone()
            
        print("Found:", counsellor['id'] if counsellor else None)
        
        students = conn.execute('''
            SELECT DISTINCT s.* 
            FROM Student s
            JOIN Appointment a ON s.id = a.student_id
            WHERE a.Counsellor_id = ?
            ORDER BY a.date DESC
        ''', (counsellor['id'],)).fetchall()
        
        print(f"Found {len(students)} cases for {user_full_name}")

    except Exception as e:
        print("Error:", repr(e))
    finally:
        conn.close()

if __name__ == '__main__':
    check_db()
