# 🎓 AAMUSTED Counselling System - Complete Deployment Package

## 📦 What's Included

This ZIP file contains everything you need to deploy the AAMUSTED Counselling System on any Windows PC.

### 🚀 Quick Start (2 minutes)
1. **Extract** this ZIP file to any folder
2. **Run** `install_dependencies.bat` (installs Python packages)
3. **Run** `QUICK_START.bat` (starts the system)
4. **Open** http://localhost:5000 in your browser

### 📁 Package Contents

```
AAMUSTED_Counselling_Deployment_Package/
├── 📄 app.py                          # Main Flask application
├── 📄 auto_report_writer.py          # Report generation module
├── 📄 windows_service.py            # Windows service implementation
├── 📄 check_service.py               # Service diagnostic tool
├── 📄 counseling.db                 # SQLite database (ready to use)
├── 📁 static/                        # CSS, JS, images
├── 📁 templates/                     # HTML templates
├── 📄 service_requirements.txt      # Python dependencies list
├── 📄 INSTALLATION_GUIDE.md         # Detailed installation guide
├── 📄 QUICK_START.bat               # Quick start script
├── 📄 install_dependencies.bat      # Dependency installer
├── 📄 install_service_admin.bat     # Service installer (admin)
├── 📄 VERIFY_PACKAGE.bat            # Package verification tool
└── 🏃‍♂️ More batch files for easy management
```

### 🎯 Features Ready to Use

✅ **Student Management** - Add, edit, view student records  
✅ **Appointment Scheduling** - Schedule counseling appointments  
✅ **Session Notes** - Record counseling sessions  
✅ **DASS-21 Assessment** - Mental health screening tool  
✅ **Case Management** - Track cases and referrals  
✅ **Report Generation** - Automated daily/weekly/monthly reports  
✅ **Statistics Dashboard** - Visual analytics and insights  
✅ **Print Functionality** - Print forms and reports  
✅ **Windows Service** - Auto-start and background operation  

### 🔧 Installation Options

#### Option 1: Quick Start (Recommended)
```cmd
install_dependencies.bat
QUICK_START.bat
```

#### Option 2: Windows Service (Auto-start)
1. Run Command Prompt as **Administrator**
2. `install_dependencies.bat`
3. `install_service_admin.bat` (right-click → Run as admin)
4. Service starts automatically on boot

#### Option 3: Manual Service Installation
```cmd
# As Administrator:
python windows_service.py install
net start AAMUSTEDCounsellingService
```

### 🌐 Access the System

Once running:
- **Web Interface**: http://localhost:5000
- **Default Port**: 5000
- **Service Name**: AAMUSTEDCounsellingService

### 🛠️ Management Commands

```cmd
# Check system status
python check_service.py

# Start/stop service (as admin)
net start AAMUSTEDCounsellingService
net stop AAMUSTEDCounsellingService

# Verify package integrity
VERIFY_PACKAGE.bat
```

### 🔒 Security & Configuration

- Runs on localhost (127.0.0.1) - no external access
- SQLite database for local storage
- No internet connection required
- Service runs with local system privileges

### 📊 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8+ (auto-installed if missing)
- **RAM**: 2GB minimum
- **Disk**: 500MB free space
- **Privileges**: Admin only for service installation

### 🆘 Troubleshooting

If something goes wrong:
1. **Run**: `VERIFY_PACKAGE.bat` (checks all files)
2. **Check**: Windows Event Viewer for service errors
3. **Test**: Direct application start with `python app.py`
4. **Diagnose**: Use `python check_service.py`

### 📞 Support

Common fixes:
- **Port 5000 in use**: Kill process or change port in `app.py`
- **Missing dependencies**: Run `install_dependencies.bat` again
- **Service won't start**: Check Event Viewer, reinstall as admin
- **Database issues**: System auto-creates tables on first run

---

## 🎉 Ready to Deploy!

**No configuration needed** - everything is pre-configured and ready to run!

1. Extract ZIP
2. Run `install_dependencies.bat`
3. Run `QUICK_START.bat`
4. Open browser to http://localhost:5000

**Total setup time: ~2 minutes**

---

*For detailed instructions, see `INSTALLATION_GUIDE.md` inside the package.*