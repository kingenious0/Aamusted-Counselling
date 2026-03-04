#!/usr/bin/env python
"""
Password Reset Script for AAMUSTED Counselling System
Resets the login password to the default: Counsellor123
"""

import sqlite3
import os
import sys
from werkzeug.security import generate_password_hash

def reset_password():
    """Reset password to default Counsellor123"""
    
    # Get database path
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(base_path, 'counseling.db')
    
    print(f'Database path: {db_path}')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print('ERROR: Database does not exist!')
        print('Please run the application first to create the database.')
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if app_settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
        if not cursor.fetchone():
            print('ERROR: app_settings table does not exist!')
            print('Please run the application first to initialize the database.')
            conn.close()
            return False
        
        # Generate new hash for Counsellor123
        default_password = 'Counsellor123'
        new_hash = generate_password_hash(default_password)
        
        print(f'\nGenerating new password hash for: {default_password}')
        
        # Check if password_hash row exists
        cursor.execute("SELECT setting_value FROM app_settings WHERE setting_name='password_hash'")
        existing = cursor.fetchone()
        
        if existing:
            print('Found existing password hash - updating...')
            cursor.execute(
                "UPDATE app_settings SET setting_value = ? WHERE setting_name = 'password_hash'",
                (new_hash,)
            )
        else:
            print('No existing password hash - creating new one...')
            cursor.execute(
                "INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)",
                ('password_hash', new_hash)
            )
        
        conn.commit()
        
        # Verify the change
        cursor.execute("SELECT setting_value FROM app_settings WHERE setting_name='password_hash'")
        verify = cursor.fetchone()
        
        if verify:
            print('\n✓ Password reset successful!')
            print(f'✓ New password: {default_password}')
            print('✓ You can now log in with this password.')
        else:
            print('\n✗ ERROR: Password reset failed - could not verify change')
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'\n✗ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('AAMUSTED Counselling System - Password Reset')
    print('=' * 60)
    print()
    
    success = reset_password()
    
    print()
    print('=' * 60)
    
    if success:
        print('Password has been reset to: Counsellor123')
        print('(Capital C, double L)')
    else:
        print('Password reset failed. Check error messages above.')
    
    print('=' * 60)
    
    sys.exit(0 if success else 1)
