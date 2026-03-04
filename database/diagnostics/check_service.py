#!/usr/bin/env python
"""
Quick service status checker for AAMUSTED Counselling System
"""

import subprocess
import sys
import os

def check_service_status():
    """Check if the service is installed and running"""
    try:
        # Check if service exists
        result = subprocess.run(
            ['sc', 'query', 'AAMUSTEDCounsellingService'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Service is not installed")
            return False
        
        # Parse the output to find the state
        lines = result.stdout.split('\n')
        for line in lines:
            if 'STATE' in line:
                if 'RUNNING' in line:
                    print("✅ Service is RUNNING")
                    return True
                elif 'STOPPED' in line:
                    print("⚠️  Service is STOPPED")
                    return False
                elif 'START_PENDING' in line:
                    print("🔄 Service is STARTING")
                    return False
                elif 'STOP_PENDING' in line:
                    print("🔄 Service is STOPPING")
                    return False
        
        print("❓ Service status unknown")
        return False
        
    except Exception as e:
        print(f"❌ Error checking service status: {e}")
        return False

def check_port_5000():
    """Check if port 5000 is in use"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True
        )
        
        if ':5000' in result.stdout:
            print("✅ Port 5000 is in use (Flask may be running)")
            return True
        else:
            print("⚠️  Port 5000 is not in use")
            return False
            
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def main():
    print("🔍 AAMUSTED Counselling System - Service Status Check")
    print("=" * 60)
    
    print("\n📋 Service Status:")
    service_running = check_service_status()
    
    print("\n🔌 Port 5000 Status:")
    port_in_use = check_port_5000()
    
    print("\n📊 Summary:")
    if service_running:
        print("✅ The counselling system service is running!")
        if port_in_use:
            print("✅ The application should be accessible at http://localhost:5000")
        else:
            print("⚠️  Service is running but port 5000 is not responding")
    else:
        print("⚠️  The counselling system service is not running")
        print("💡 To start the service, run: net start AAMUSTEDCounsellingService")
        print("💡 Or use the service manager: python service_manager.py")

if __name__ == '__main__':
    main()