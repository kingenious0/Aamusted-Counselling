# 📦 Deploying to Another PC - Complete Guide

## 🎯 What You Need to Transfer

You need to copy the **entire project folder** to her PC:

```
Counselling System -Remade\
```

Transfer this whole folder to her PC (e.g., to `C:\AAMUSTED Counselling\` or her Desktop).

---

## 📋 Step-by-Step Deployment Process

### STEP 1: Transfer Files to Her PC

**Option A - USB Drive:**
1. Copy the entire `Counselling System -Remade` folder to a USB drive
2. Plug USB into her PC
3. Copy the folder to her PC (recommended location: `C:\AAMUSTED Counselling\`)

**Option B - Network/Cloud:**
1. Zip the entire folder
2. Transfer via OneDrive, Google Drive, or network share
3. Extract on her PC

---

### STEP 2: Install Python (If Not Already Installed)

On her PC:

1. **Check if Python is installed:**
   - Open Command Prompt (press `Win + R`, type `cmd`, press Enter)
   - Type: `python --version`
   - If you see "Python 3.x.x", skip to STEP 3
   - If you see an error, continue below

2. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Download Python 3.11 or newer
   - Run the installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
   - Click "Install Now"

---

### STEP 3: Install Dependencies

On her PC:

1. **Open Command Prompt as Administrator:**
   - Press `Win + X`
   - Select "Command Prompt (Admin)" or "Windows PowerShell (Admin)"

2. **Navigate to the project folder:**
   ```cmd
   cd "C:\AAMUSTED Counselling"
   ```
   *(Replace with wherever you copied the folder)*

3. **Install required packages:**
   ```cmd
   pip install -r requirements.txt
   ```

   Wait for installation to complete (may take 2-5 minutes).

---

### STEP 4: Reset Password (First Time Setup)

Still in the Command Prompt (in the project folder):

```cmd
python reset_password.py
```

You should see:
```
✓ Password reset successful!
✓ New password: Counsellor123
```

---

### STEP 5: Install Auto-Start Service

**This is the key step for background auto-start!**

1. **In File Explorer, navigate to the project folder**

2. **Find the file:** `SETUP_AUTO_START.bat`

3. **Right-click** on it

4. **Select "Run as administrator"**

5. **Follow the prompts** - it will:
   - Install the Windows Service
   - Start it immediately
   - Configure auto-start on boot

6. **You should see:**
   ```
   [OK] Service installed successfully!
   [OK] Service started successfully!
   SUCCESS! The counselling system is now running.
   ```

---

### STEP 6: Test the System

On her PC:

1. **Open any web browser** (Chrome, Edge, Firefox, etc.)

2. **Go to:** http://localhost:5000

3. **Enter password:** `Counsellor123`

4. **You should see the dashboard!** ✓

---

## ✅ Verification Checklist

After setup on her PC, verify:

- [ ] Python is installed: `python --version`
- [ ] Dependencies installed: `pip list` shows Flask, etc.
- [ ] Password reset completed successfully
- [ ] Service installed: `sc query AAMUSTEDCounsellingService`
- [ ] Service is running: Shows `STATE: 4 RUNNING`
- [ ] Can access http://localhost:5000 in browser
- [ ] Can log in with `Counsellor123`
- [ ] No CMD window visible (runs in background)

---

## 🔄 What Happens After Reboot?

After her PC restarts:

✅ **Service starts automatically** (no manual action needed)  
✅ **Runs in background** (no visible window)  
✅ **System is accessible** at http://localhost:5000  
✅ **Just open browser** and go to http://localhost:5000  

---

## 🛠️ Troubleshooting on Her PC

### Problem: "Python is not recognized"

**Solution:**
- Python not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Or download and use the portable Python version

---

### Problem: "pip install" fails

**Solution:**
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### Problem: Service won't install - "Access denied"

**Solution:**
- Must run `SETUP_AUTO_START.bat` as Administrator
- Right-click → "Run as administrator"

---

### Problem: Port 5000 already in use

**Solution:**
1. Check what's using it:
   ```cmd
   netstat -ano | findstr :5000
   ```

2. Kill that process or change the port in `windows_service.py` (line 127):
   ```python
   self.server = make_server('127.0.0.1', 5000, app, threaded=True)
   ```
   Change `5000` to another port like `8080`

---

### Problem: Can't access http://localhost:5000

**Solutions:**

1. **Check if service is running:**
   ```cmd
   sc query AAMUSTEDCounsellingService
   ```

2. **If not running, start it:**
   ```cmd
   net start AAMUSTEDCounsellingService
   ```

3. **Check firewall:**
   - Windows Firewall might be blocking it
   - Add exception for Python or the service

4. **Check service logs:**
   - Open folder: `service_logs\`
   - Check latest log file for errors

---

## 📱 Quick Reference Card (Print This for Her)

```
═══════════════════════════════════════════════════════════
    AAMUSTED COUNSELLING SYSTEM - QUICK REFERENCE
═══════════════════════════════════════════════════════════

🌐 ACCESS THE SYSTEM:
   1. Open any web browser
   2. Go to: http://localhost:5000
   3. Password: Counsellor123

🔄 RESTART THE SERVICE:
   1. Press Win + X
   2. Select "Command Prompt (Admin)"
   3. Type: net stop AAMUSTEDCounsellingService
   4. Type: net start AAMUSTEDCounsellingService

✅ CHECK IF RUNNING:
   1. Press Win + X
   2. Select "Command Prompt (Admin)"
   3. Type: sc query AAMUSTEDCounsellingService
   4. Look for "STATE: 4 RUNNING"

🛑 STOP THE SERVICE:
   net stop AAMUSTEDCounsellingService

▶️ START THE SERVICE:
   net start AAMUSTEDCounsellingService

📁 PROJECT LOCATION:
   C:\AAMUSTED Counselling\

═══════════════════════════════════════════════════════════
```

---

## 🎯 Summary: What to Do on Her PC

1. **Copy** entire project folder to her PC
2. **Install** Python (if needed)
3. **Run** `pip install -r requirements.txt`
4. **Run** `python reset_password.py`
5. **Right-click** `SETUP_AUTO_START.bat` → "Run as administrator"
6. **Test** by opening http://localhost:5000
7. **Done!** System runs automatically from now on

---

## 💾 Files You Must Include When Transferring

Make sure these files are in the folder you transfer:

✅ `app.py` - Main application  
✅ `windows_service.py` - Service implementation  
✅ `requirements.txt` - Dependencies list  
✅ `reset_password.py` - Password reset tool  
✅ `SETUP_AUTO_START.bat` - Auto-start installer  
✅ `REMOVE_AUTO_START.bat` - Uninstaller  
✅ `counseling.db` - Database (or it will be created)  
✅ `templates\` folder - HTML templates  
✅ `static\` folder - CSS, images, etc.  
✅ All other `.py` files  

**Basically: Transfer the ENTIRE folder!**

---

## 📞 Support

If issues occur on her PC:
1. Check `service_logs\` folder for error messages
2. Run `python check_service.py` for diagnostics
3. Check Windows Event Viewer for service errors

---

**Last Updated:** 2025-11-30  
**Default Password:** Counsellor123  
**Access URL:** http://localhost:5000
