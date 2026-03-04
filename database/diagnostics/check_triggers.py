import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for triggers
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger';")
triggers = cursor.fetchall()

print("Triggers in the database:")
for trigger in triggers:
    print(f"- {trigger[0]}")
    if trigger[1]:
        print(f"  SQL: {trigger[1][:200]}...")

# Check for views
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view';")
views = cursor.fetchall()

print("\nViews in the database:")
for view in views:
    print(f"- {view[0]}")
    if view[1]:
        print(f"  SQL: {view[1][:200]}...")

# Check if there are any references to 'appointments' in the database schema
cursor.execute("SELECT name, type, sql FROM sqlite_master WHERE sql LIKE '%appointments%';")
references = cursor.fetchall()

print("\nDatabase objects referencing 'appointments':")
for ref in references:
    print(f"- {ref[0]} ({ref[1]})")
    if ref[2]:
        # Find the line with 'appointments'
        lines = ref[2].split('\n')
        for line in lines:
            if 'appointments' in line.lower():
                print(f"  Line: {line.strip()}")

conn.close()