import sqlite3

def upgrade_db():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE Appointment ADD COLUMN urgency TEXT")
        print("Added urgency column")
    except Exception as e:
        print(f"urgency column might already exist: {e}")
        
    try:
        cursor.execute("ALTER TABLE Appointment ADD COLUMN referral_source TEXT")
        print("Added referral_source column")
    except Exception as e:
        print(f"referral_source column might already exist: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    upgrade_db()
