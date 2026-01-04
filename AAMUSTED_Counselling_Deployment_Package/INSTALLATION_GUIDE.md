# AAMUSTED Counselling System - Deployment Package

## 🎯 Quick Start Guide

This package contains everything needed to deploy the AAMUSTED Counselling System on a new PC.

### 📋 Prerequisites
- Windows 10/11 (64-bit)
- Python 3.8+ (recommended: 3.11+)
- Administrator privileges (for service installation)

### 🚀 Installation Steps

#### Step 1: Install Python
1. Download Python from https://python.org
2. Install with "Add Python to PATH" checked
3. Verify installation: `python --version`

#### Step 2: Install Dependencies
Run the dependency installation script:
```cmd
pip install -r service_requirements.txt
```

#### Step 3: Test the Application
Run the Flask application directly:
```cmd
python app.py
```
Open http://localhost:5000 in your browser to verify it works.

#### Step 4: Install Windows Service (Optional)
**For automatic startup and background operation:**

1. **Run as Administrator**: Right-click Command Prompt → "Run as administrator"
2. **Navigate to this folder**: `cd "path\to\this\folder"`
3. **Install service**: `python windows_service.py install`
4. **Start service**: `net start AAMUSTEDCounsellingService`

### 📁 Package Contents

```
AAMUSTED_Counselling_Deployment_Package/
├── 📄 app.py                          # Main Flask application
├── 📄 auto_report_writer.py           # Report generation module
├── 📄 check_service.py               # Service diagnostic tool
├── 📄 service_manager.py             # Service management utility
├── 📄 windows_service.py            # Windows service implementation
├── 📄 counseling.db                  # SQLite database
├── 📄 requirements.txt               # Python dependencies
├── 📄 service_requirements.txt       # Service-specific dependencies
├── 📁 static/                        # CSS, JS, images
├── 📁 templates/                     # HTML templates
├── 📁 install_service_admin.bat     # Admin installation script
├── 📁 install_service.bat            # Service installation
├── 📁 uninstall_service.bat          # Service removal
├── 📁 START_SYSTEM.bat               # Quick start script
└── 📁 START_SYSTEM_WITH_PYTHON.bat # Alternative start script
```

### 🔧 Management Commands

#### Application Management
```cmd
# Start application directly
python app.py

# Test all endpoints
python test_system.py

# Check service status
python check_service.py
```

#### Service Management (Run as Administrator)
```cmd
# Install service
python windows_service.py install

# Start service
net start AAMUSTEDCounsellingService

# Stop service
net stop AAMUSTEDCounsellingService

# Check service status
sc query AAMUSTEDCounsellingService

# Uninstall service
python windows_service.py uninstall
```

### 🌐 Accessing the System

Once installed and running:
- **Web Interface**: http://localhost:5000
- **Default Port**: 5000
- **Service Name**: AAMUSTEDCounsellingService

### 🛠️ Troubleshooting

#### Common Issues

1. **Port 5000 Already in Use**
   ```cmd
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   ```

2. **Service Won't Start**
   - Check Windows Event Viewer
   - Run `python check_service.py`
   - Verify all dependencies installed

3. **Import Errors**
   - Reinstall dependencies: `pip install -r service_requirements.txt`
   - Verify Python version compatibility

4. **Database Issues**
   - The system will create necessary tables automatically
   - Check `counseling.db` file permissions

#### Verification Steps

1. **Test Flask Application**:
   ```cmd
   python app.py
   ```
   Should start server on http://localhost:5000

2. **Test Service Installation**:
   ```cmd
   python check_service.py
   ```
   Should show service status and port availability

3. **Check Dependencies**:
   ```cmd
   python -c "import flask, win32serviceutil, apscheduler, docx; print('All dependencies OK')"
   ```

### 📊 System Features

- **Student Management**: Add, edit, view student records
- **Appointment Scheduling**: Schedule and manage appointments
- **Session Notes**: Record counseling sessions
- **DASS-21 Assessment**: Mental health screening
- **Case Management**: Track case notes and referrals
- **Report Generation**: Automated reports (daily, weekly, monthly)
- **Statistics Dashboard**: Visual analytics and insights
- **Print Functionality**: Print forms and reports
- **Windows Service**: Auto-start and background operation

### 🔒 Security Notes

- Default configuration uses localhost (127.0.0.1)
- SQLite database for local storage
- No external network access required
- Service runs with local system privileges

### 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run diagnostic tools: `python check_service.py`
3. Check Windows Event Viewer for service errors
4. Verify all files are present and not corrupted

### 🔄 Updates

To update the system:
1. Stop the service (if running)
2. Replace application files
3. Restart the service
4. Test functionality

---

**Ready to deploy!** 🎉

The system is now ready for installation on any Windows PC with Python 3.8+.