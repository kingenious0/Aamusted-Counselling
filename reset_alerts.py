
import sqlite3

def reset():
    conn = sqlite3.connect('counseling.db')
    conn.execute("INSERT OR REPLACE INTO app_settings (setting_name, setting_value) VALUES ('pending_booking_alert', 'false')")
    conn.commit()
    print("Alerts reset to false.")
    conn.close()

if __name__ == '__main__':
    reset()
