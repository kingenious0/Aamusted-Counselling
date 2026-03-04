IMPORTANT: DELETE FUNCTIONALITY REQUIRES SERVER RESTART
========================================================

NEW DELETE FEATURES ADDED:
---------------------------
✓ Delete Students (with all related records)
✓ Delete Appointments (with related sessions)
✓ Delete Sessions (with related referrals)
✓ Delete Referrals

HOW TO USE DELETE FEATURES:
---------------------------
1. STOP the current server:
   - Close any running EXE or terminal windows
   - Or press Ctrl+C in the terminal running the server

2. RESTART using Python script (not EXE):
   - Double-click: START_SYSTEM.bat
   - OR run: python app.py
   - OR use: RESTART_FOR_DELETE.bat

3. The delete buttons will now work!

WHY THE RESTART?
----------------
The EXE file was compiled before delete routes were added.
You MUST use the Python script to get the latest features.

DELETE BUTTON LOCATIONS:
-------------------------
• Students: All Students page → Red trash icon
• Appointments: Manage Appointments → Dropdown menu → Delete
• Sessions: All Sessions page → Red trash icon
• Referrals: All Referrals page → Red trash icon

All deletions include:
- Confirmation dialogs
- Automatic cleanup of related records
- Success/error messages

COUNSELLOR SETUP:
-----------------
The system is configured for:
• Mrs. Gertrude Effeh Brew (only counsellor)

To update existing database, run:
python update_counsellor_db.py

