import sqlite3, os, re
from datetime import datetime

def clean_date(val):
    if not val: return val
    raw = str(val)
    # 1. Thu, 19 Mar 2026 00:00:00 GMT -> 2026-03-19
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', raw)
    if iso_match: return iso_match.group(1)
    
    clean_str = raw.replace(' GMT', '').replace(',', '')
    parts = clean_str.split(' ')
    if len(parts) >= 4:
        try:
            day_str = f"{parts[1]} {parts[2]} {parts[3]}"
            d_obj = datetime.strptime(day_str, '%d %b %Y')
            return d_obj.strftime('%Y-%m-%d')
        except: pass
    return val

def clean_timestamp(val):
    if not val: return val
    raw = str(val)
    # 2. Wed, 18 Mar 2026 18:20:40 GMT -> 2026-03-18 18:20:40
    iso_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', raw)
    if iso_match: return iso_match.group(1)
    
    clean_str = raw.replace(' GMT', '').replace(',', '')
    parts = clean_str.split(' ')
    if len(parts) >= 5:
        try:
            ts_str = f"{parts[1]} {parts[2]} {parts[3]} {parts[4]}"
            d_obj = datetime.strptime(ts_str, '%d %b %Y %H:%M:%S')
            return d_obj.strftime('%Y-%m-%d %H:%M:%S')
        except: pass
    return val

db_path = 'counseling.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Cleaning Appointment dates...")
apps = cursor.execute("SELECT id, date FROM Appointment WHERE date LIKE '%,%'").fetchall()
for id, d in apps:
    new_d = clean_date(d)
    if new_d != d:
        cursor.execute("UPDATE Appointment SET date = ? WHERE id = ?", (new_d, id))

print("Cleaning session created_at...")
sess = cursor.execute("SELECT id, created_at FROM session WHERE created_at LIKE '%,%'").fetchall()
for id, ts in sess:
    new_ts = clean_timestamp(ts)
    if new_ts != ts:
        cursor.execute("UPDATE session SET created_at = ? WHERE id = ?", (new_ts, id))

print("Cleaning BookingRequest preferred_date and created_at...")
bookings = cursor.execute("SELECT id, preferred_date, created_at FROM BookingRequest WHERE preferred_date LIKE '%,%' OR created_at LIKE '%,%'").fetchall()
for id, pd, ca in bookings:
    new_pd = clean_date(pd)
    new_ca = clean_timestamp(ca)
    cursor.execute("UPDATE BookingRequest SET preferred_date = ?, created_at = ? WHERE id = ?", (new_pd, new_ca, id))

conn.commit()
conn.close()
print("Migration Finished.")
