import sqlite3
import sys

# Test the dashboard query directly
def test_dashboard_query():
    try:
        conn = sqlite3.connect('counseling.db')
        conn.row_factory = sqlite3.Row
        
        # Test the exact query from the dashboard function
        query = '''
            SELECT a.id, a.date, a.time, a.purpose, a.status,
                   s.name as student_name,
                   c.name as counsellor_name
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            JOIN Counsellor c ON a.counselor_id = c.id
            WHERE a.date >= DATE('now')
            ORDER BY a.date, a.time
            LIMIT 10
        '''
        
        print("Testing dashboard query...")
        print("Query:", query)
        
        appointments = conn.execute(query).fetchall()
        print(f"✓ Success: Found {len(appointments)} appointments")
        
        for apt in appointments:
            print(f"  - {apt['student_name']}: {apt['date']} {apt['time']} ({apt['purpose']})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard_query()
    sys.exit(0 if success else 1)