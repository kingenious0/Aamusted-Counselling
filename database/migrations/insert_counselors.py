import sqlite3

def insert_Counsellors():
    conn = sqlite3.connect('counseling.db')
    cursor = conn.cursor()

    # Only Mrs. Gertrude Effeh Brew
    Counsellors_to_insert = [
        (1, 'Mrs. Gertrude Effeh Brew', '')
    ]
    
    # Delete all existing counsellors except the one we want to keep
    cursor.execute("DELETE FROM Counsellor WHERE id != 1 OR name != 'Mrs. Gertrude Effeh Brew'")

    for Counsellor in Counsellors_to_insert:
        try:
            cursor.execute('INSERT INTO Counsellor (id, name, contact) VALUES (?, ?, ?)', Counsellor)
            print(f"Inserted Counsellor: {Counsellor[1]}")
        except sqlite3.IntegrityError:
            print(f"Counsellor {Counsellor[1]} (ID: {Counsellor[0]}) already exists, skipping.")

    conn.commit()
    conn.close()
    print('Counsellor insertion process completed.')

if __name__ == '__main__':
    insert_Counsellors()