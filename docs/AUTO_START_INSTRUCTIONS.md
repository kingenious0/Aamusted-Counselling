# AAMUSTED Counselling System - Auto-Start Setup Guide

## ✅ Password Fixed!

Your login password has been reset to: **`Counsellor123`** (Capital C, double L)

You can now log in successfully at http://localhost:5000

---

## 🚀 Setting Up Auto-Start (Background Service)

To make the counselling system run automatically in the background when your PC boots (with NO visible CMD window):

### Quick Setup (Recommended)

1. **Right-click** on `SETUP_AUTO_START.bat`
2. Select **"Run as administrator"**
3. Follow the prompts
4. Done! ✓

The system will now:
- ✓ Run silently in the background (no CMD window)
- ✓ Start automatically when Windows boots
- ✓ Restart automatically if it crashes
- ✓ Be accessible at http://localhost:5000

---

## 📋 Service Management

### Check if Service is Running

Open Command Prompt and run:
```cmd
sc query AAMUSTEDCounsellingService
```

Look for `STATE: 4 RUNNING` in the output.

### Start the Service Manually

```cmd
net start AAMUSTEDCounsellingService
```

### Stop the Service

```cmd
net stop AAMUSTEDCounsellingService
```

### Remove Auto-Start

1. **Right-click** on `REMOVE_AUTO_START.bat`
2. Select **"Run as administrator"**
3. Follow the prompts

---

## 🔍 Troubleshooting

### Service Won't Install

**Problem:** "Access is denied" error

**Solution:** You must run the batch file as Administrator:
1. Right-click `SETUP_AUTO_START.bat`
2. Select "Run as administrator"

---

### Service Won't Start

**Problem:** Service installs but won't start

**Solutions:**

1. **Check if port 5000 is already in use:**
   ```cmd
   netstat -ano | findstr :5000
   ```
   If something is using port 5000, stop it first.

2. **Check service logs:**
   - Open folder: `service_logs\`
   - Look at the latest log file: `counselling_service_YYYYMMDD.log`
   - Check for error messages

3. **Verify Python dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

---

### Can't Access http://localhost:5000

**Problem:** Browser says "Can't connect"

**Solutions:**

1. **Check if service is running:**
   ```cmd
   sc query AAMUSTEDCounsellingService
   ```
   Should show `STATE: 4 RUNNING`

2. **If not running, start it:**
   ```cmd
   net start AAMUSTEDCounsellingService
   ```

3. **Check service logs** in `service_logs\` folder

---

### Password Still Not Working

If `Counsellor123` still doesn't work after the reset:

1. Run `reset_password.py` again:
   ```cmd
   python reset_password.py
   ```

2. Restart the service:
   ```cmd
   net stop AAMUSTEDCounsellingService
   net start AAMUSTEDCounsellingService
   ```

3. Try logging in again with: **`Counsellor123`**

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `SETUP_AUTO_START.bat` | Install and start the background service |
| `REMOVE_AUTO_START.bat` | Stop and uninstall the background service |
| `reset_password.py` | Reset login password to `Counsellor123` |
| `windows_service.py` | Windows Service implementation |
| `service_logs\` | Service log files (for troubleshooting) |

---

## 🎯 Quick Reference

### After Setup, Your System Will:

✓ **Start automatically** when Windows boots  
✓ **Run in background** with no visible window  
✓ **Auto-restart** if it crashes  
✓ **Be accessible** at http://localhost:5000  
✓ **Log everything** to `service_logs\` folder  

### To Access the System:

1. Open any web browser
2. Go to: http://localhost:5000
3. Enter password: **`Counsellor123`**
4. Done!

---

## 🛠️ Advanced: Manual Service Commands

If you prefer using Command Prompt directly (must run as Administrator):

```cmd
# Install service
python windows_service.py install

# Start service
net start AAMUSTEDCounsellingService

# Stop service
net stop AAMUSTEDCounsellingService

# Check status
sc query AAMUSTEDCounsellingService

# Uninstall service
python windows_service.py uninstall
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Service is installed: `sc query AAMUSTEDCounsellingService`
- [ ] Service is running: Look for `STATE: 4 RUNNING`
- [ ] Can access http://localhost:5000 in browser
- [ ] Can log in with password: `Counsellor123`
- [ ] No CMD window is visible
- [ ] After reboot, service starts automatically

---

## 📞 Need Help?

1. Check service logs in `service_logs\` folder
2. Run diagnostic: `python check_service.py`
3. Check Windows Event Viewer → Windows Logs → Application
   - Look for "AAMUSTEDCounsellingService" entries

---

**Last Updated:** 2025-11-30  
**Password:** Counsellor123 (Capital C, double L)  
**Access URL:** http://localhost:5000
