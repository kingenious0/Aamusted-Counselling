import sqlite3
import uuid
import os

db_path = 'counseling.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Update logo_url setting
    # UPSERT syntax for SQLite
    cur.execute("""
        INSERT INTO app_settings (setting_name, setting_value, global_id, updated_at) 
        VALUES ('logo_url', '/assets/aamusted_logo.png', ?, CURRENT_TIMESTAMP)
        ON CONFLICT(setting_name) DO UPDATE SET 
            setting_value = excluded.setting_value,
            updated_at = excluded.updated_at
    """, (str(uuid.uuid4()),))
    
    # Also update system_name if needed, or just keep it
    
    conn.commit()
    conn.close()
    print("Logo updated successfully in database.")
else:
    print("Database not found.")
