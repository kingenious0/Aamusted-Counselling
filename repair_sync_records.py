import sqlite3

db_path = 'counseling.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Find unsynced students
cur.execute("SELECT name, updated_at, last_synced_at FROM Student WHERE last_synced_at IS NULL")
rows = cur.fetchall()

print(f"Unsynced students ({len(rows)}):")
for r in rows:
    print(f" - {r[0]} | Updated: {r[1]} | Synced: {r[2]}")

# REPAIR: If updated_at is NULL, set it to now to force a sync
cur.execute("UPDATE Student SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
# Also global_id
import uuid
cur.execute("SELECT id FROM Student WHERE global_id IS NULL")
ids = [r[0] for r in cur.fetchall()]
for rid in ids:
    cur.execute("UPDATE Student SET global_id = ? WHERE id = ?", (str(uuid.uuid4()), rid))

conn.commit()
conn.close()
print("Local unsynced records repaired. They will sync in the next cycle.")
