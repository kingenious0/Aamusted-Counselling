"""
Utility script to update the database to have only Mrs. Gertrude Effeh Brew as counsellor
"""
import sqlite3
import os

def update_counsellors():
    """Update database to have only Mrs. Gertrude Effeh Brew as counsellor"""
    db_path = 'counseling.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Update or insert Mrs. Gertrude Effeh Brew
        cursor.execute('''
            INSERT OR REPLACE INTO Counsellor (id, name, contact)
            VALUES (1, 'Mrs. Gertrude Effeh Brew', '')
        ''')
        
        # Delete any other counsellors
        cursor.execute("DELETE FROM Counsellor WHERE id != 1")
        
        # Update all existing appointments to use Mrs. Gertrude Effeh Brew (ID 1)
        cursor.execute('''
            UPDATE Appointment 
            SET counselor_id = 1 
            WHERE counselor_id IS NULL OR counselor_id NOT IN (SELECT id FROM Counsellor)
        ''')
        
        conn.commit()
        
        # Verify
        counsellors = cursor.execute('SELECT * FROM Counsellor').fetchall()
        print(f"\n✅ Database updated successfully!")
        print(f"\nCurrent Counsellors in database:")
        for counsellor in counsellors:
            print(f"  - ID {counsellor[0]}: {counsellor[1]}")
        
        if len(counsellors) == 1 and counsellors[0][1] == 'Mrs. Gertrude Effeh Brew':
            print("\n✅ Perfect! Only Mrs. Gertrude Effeh Brew is now in the system.")
        else:
            print("\n⚠️  Warning: Expected only Mrs. Gertrude Effeh Brew, but found others.")
            
    except Exception as e:
        print(f"\n❌ Error updating database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Updating Counsellor Database")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Set Mrs. Gertrude Effeh Brew as the only counsellor")
    print("  2. Update all appointments to use her")
    print("  3. Remove any other counsellors from the database")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        exit(0)
    
    update_counsellors()

