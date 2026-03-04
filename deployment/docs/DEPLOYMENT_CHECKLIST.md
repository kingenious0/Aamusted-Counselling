# AAMUSTED Counselling System - Deployment Checklist for Counselor's PC

## 📋 Pre-Deployment Checklist

### System Requirements Verification
- [ ] Windows 7/8/10/11 or Windows Server 2012+
- [ ] At least 2GB RAM available
- [ ] 500MB free disk space
- [ ] Administrator account access

### Files to Transfer
Copy these files to the counselor's PC:
- [ ] `app.py` (main application)
- [ ] `database.db` (SQLite database)
- [ ] `templates/` folder (all HTML files)
- [ ] `static/` folder (CSS, JS, images)
- [ ] `windows_service.py` (service wrapper)
- [ ] `service_manager.py` (management tool)
- [ ] `install_service.bat` (installer)
- [ ] `uninstall_service.bat` (uninstaller)
- [ ] `check_service.py` (status checker)
- [ ] `service_requirements.txt` (dependencies)

## 🚀 Deployment Process

### Step 1: File Transfer
```
Create folder: C:\AAMUSTED_Counselling\
Copy all application files to this folder
```

### Step 2: Python Installation Check
```cmd
# Check if Python is installed
python --version

# If not installed, download from https://www.python.org/
# Install Python 3.7 or higher
# IMPORTANT: Check "Add Python to PATH" during installation
```

### Step 3: Install Dependencies
```cmd
# Open Command Prompt as Administrator
cd C:\AAMUSTED_Counselling\

# Install required packages
python -m pip install pywin32
```

### Step 4: Install Service
```cmd
# Right-click on install_service.bat
# Select "Run as administrator"
# Follow the prompts
```

### Step 5: Verify Installation
```cmd
# Check service status
python check_service.py

# Alternative check
sc query AAMUSTEDCounsellingService
```

### Step 6: Test the Application
```
Open browser: http://localhost:5000
Should see the AAMUSTED Counselling System login page
```

## 🔧 Post-Deployment Verification

### Immediate Checks (After Installation)
- [ ] Service shows as "RUNNING" in status check
- [ ] Browser can access http://localhost:5000
- [ ] Login page displays correctly
- [ ] No error messages in service logs

### 24-Hour Checks
- [ ] Service still running after reboot
- [ ] Application accessible after system startup
- [ ] No crash reports in logs
- [ ] Database connections working

### Weekly Checks
- [ ] Service logs show normal operation
- [ ] Database backup created
- [ ] No performance issues reported
- [ ] System resources adequate

## 🛠️ Troubleshooting on Counselor's PC

### If Service Won't Install
1. **Check Administrator Rights**
   ```cmd
   # Run this command
   net session
   # Should show "The command completed successfully"
   ```

2. **Check Python Installation**
   ```cmd
   python --version
   where python
   ```

3. **Check Antivirus**
   - Temporarily disable antivirus
   - Add exception for the application folder
   - Try installation again

### If Service Won't Start
1. **Check Port 5000**
   ```cmd
   netstat -ano | findstr :5000
   ```

2. **Check Logs**
   ```cmd
   python service_manager.py
   # Select option 6 to view logs
   ```

3. **Manual Start**
   ```cmd
   net start AAMUSTEDCounsellingService
   ```

### If Application Won't Load
1. **Check Service Status**
   ```cmd
   python check_service.py
   ```

2. **Check Browser**
   - Try different browser
   - Clear cache
   - Check http://localhost:5000

3. **Check Database**
   ```cmd
   # Test database
   python -c "import sqlite3; conn = sqlite3.connect('database.db'); print('Database OK'); conn.close()"
   ```

## 📞 Support Instructions for Counselor

### Daily Operation
- **Starting PC**: Service starts automatically
- **Accessing System**: Open browser → http://localhost:5000
- **Checking Status**: Run `python check_service.py`

### If System is Down
1. **Check if service is running**: `python check_service.py`
2. **If stopped**: `net start AAMUSTEDCounsellingService`
3. **If still not working**: Contact IT support

### Emergency Restart Procedure
```cmd
# 1. Stop service
net stop AAMUSTEDCounsellingService

# 2. Wait 10 seconds

# 3. Start service
net start AAMUSTEDCounsellingService

# 4. Check status
python check_service.py
```

## 📁 File Locations on Counselor's PC

```
C:\AAMUSTED_Counselling\
├── app.py                    # Main application
├── database.db              # Database file
├── windows_service.py       # Service wrapper
├── service_manager.py       # Management tool
├── check_service.py         # Status checker
├── install_service.bat      # Installer
├── uninstall_service.bat    # Uninstaller
├── service_logs\            # Log files
├── templates\               # HTML templates
└── static\                  # CSS/JS files
```

## 🔄 Maintenance Schedule

### Daily (Automated)
- [ ] Service monitoring
- [ ] Log rotation
- [ ] Health checks

### Weekly (Manual)
- [ ] Review service logs
- [ ] Check database integrity
- [ ] Verify backup creation

### Monthly (Manual)
- [ ] System performance review
- [ ] Security updates
- [ ] Backup verification

## 🚨 Emergency Contacts

**Technical Issues**: [Your IT Support Contact]
**Service Down**: [Your Emergency Contact]
**Database Issues**: [Your Database Admin Contact]

## ✅ Final Deployment Confirmation

### Before You Leave
- [ ] Service installed and running
- [ ] Application accessible in browser
- [ ] Counselor can log in successfully
- [ ] Counselor knows how to check status
- [ ] Counselor has emergency contact information
- [ ] All documentation provided to counselor

### Documentation to Provide
1. **Quick Reference Card** (print and give to counselor)
2. **Emergency Procedures** (laminated card)
3. **Contact Information** (multiple copies)
4. **Service Status Checker** (desktop shortcut)

## 🎯 Success Criteria

✅ **Service starts automatically on boot**  
✅ **Application accessible at http://localhost:5000**  
✅ **Counselor can log in and use system**  
✅ **No manual intervention required**  
✅ **Crash recovery working**  
✅ **Comprehensive logging enabled**  

---

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Counselor Trained**: ___________  
**Next Review Date**: ___________