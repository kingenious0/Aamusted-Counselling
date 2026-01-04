# AAMUSTED Counselling System - Desktop Shortcut Creator
# This script creates desktop shortcuts for easy service management

import os
import winshell
from win32com.client import Dispatch
import sys

def create_desktop_shortcuts():
    """Create desktop shortcuts for service management"""
    
    # Get desktop path
    desktop = winshell.desktop()
    
    # Paths
    app_dir = r"C:\AAMUSTED_Counselling"
    check_script = os.path.join(app_dir, "check_service.py")
    
    # Create shortcut for service checker
    shell = Dispatch('WScript.Shell')
    
    # Shortcut 1: Check Service Status
    shortcut1 = shell.CreateShortCut(os.path.join(desktop, "Check Counselling Service.lnk"))
    shortcut1.Targetpath = sys.executable
    shortcut1.Arguments = f'"{check_script}"'
    shortcut1.WorkingDirectory = app_dir
    shortcut1.IconLocation = sys.executable
    shortcut1.save()
    
    # Shortcut 2: Service Manager
    manager_script = os.path.join(app_dir, "service_manager.py")
    shortcut2 = shell.CreateShortCut(os.path.join(desktop, "Counselling Service Manager.lnk"))
    shortcut2.Targetpath = sys.executable
    shortcut2.Arguments = f'"{manager_script}"'
    shortcut2.WorkingDirectory = app_dir
    shortcut2.IconLocation = sys.executable
    shortcut2.save()
    
    print("✅ Desktop shortcuts created successfully!")
    print("\nCreated shortcuts:")
    print("1. Check Counselling Service - Quick status check")
    print("2. Counselling Service Manager - Full management interface")
    print(f"\nShortcuts are on your desktop: {desktop}")

if __name__ == "__main__":
    try:
        create_desktop_shortcuts()
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"❌ Error creating shortcuts: {e}")
        input("\nPress Enter to exit...")