import sqlite3

def check_Counsellors():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, contact FROM Counsellor')
    Counsellors = cursor.fetchall()
    conn.close()
    if Counsellors:
        print("Counsellors in the database:")
        for Counsellor in Counsellors:
            print(f"ID: {Counsellor[0]}, Name: {Counsellor[1]}, Contact: {Counsellor[2]}")
    else:
        print("No Counsellors found in the database.")

if __name__ == '__main__':
    check_Counsellors()