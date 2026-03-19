import sqlite3
import uuid

def is_uuid(val):
    try:
        if not val: return False
        uuid.UUID(str(val))
        return True
    except:
        return False

def check_global_ids():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()
    
    tables = [
        'Student', 
        'Appointment', 
        'session', 
        'Referral', 
        'CaseManagement', 
        'OutcomeQuestionnaire', 
        'DASS21', 
        'Feedback',
        'SessionIssue',
        'Notification',
        'app_settings',
        'BookingRequest'
    ]
    
    invalid = []
    
    for table in tables:
        pk = 'id'
        if table == 'SessionIssue':
            cursor.execute(f"SELECT session_id, issue_name, global_id FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                sid, iname, global_id = row
                if not is_uuid(global_id):
                    new_id = str(uuid.uuid4())
                    cursor.execute(f"UPDATE {table} SET global_id = ? WHERE session_id = ? AND issue_name = ?", (new_id, sid, iname))
        else:
            cursor.execute(f"SELECT id, global_id FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                row_id, global_id = row
                if not is_uuid(global_id):
                    new_id = str(uuid.uuid4())
                    cursor.execute(f"UPDATE {table} SET global_id = ? WHERE id = ?", (new_id, row_id))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    check_global_ids()
