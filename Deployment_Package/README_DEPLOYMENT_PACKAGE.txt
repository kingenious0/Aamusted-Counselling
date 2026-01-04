# AAMUSTED Counselling System - Deployment Package

Created on: November 29, 2025

## 📋 What's Included

- **Application Files**: Main Flask application and database
- **Service Files**: Windows Service wrapper and management tools
- **Templates & Static Files**: Web interface components
- **Installation Scripts**: Automated deployment tools
- **Documentation**: Complete deployment and user guides

## 🚀 Quick Deployment Steps

1. **Copy this package** to the counselor's PC
2. **Extract all files** to a temporary folder
3. **Right-click** on `INSTALL_ON_COUNSELOR_PC.bat`
4. **Select "Run as administrator"**
5. **Follow the prompts** and wait for completion

## 📁 Files in Package

### Core Application
- `app.py` - Main Flask application
- `counseling.db` - SQLite database
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, images

### Service Management
- `windows_service.py` - Windows Service wrapper
- `service_manager.py` - Service management interface
- `check_service.py` - Quick status checker
- `create_shortcuts.py` - Desktop shortcut creator

### Installation
- `INSTALL_ON_COUNSELOR_PC.bat` - Main installation script
- `install_service.bat` - Alternative installer
- `uninstall_service.bat` - Service uninstaller
- `service_requirements.txt` - Python dependencies

### Documentation
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step deployment guide
- `COUNSELOR_QUICK_REFERENCE.md` - Quick reference for counselor
- `SERVICE_README.md` - Technical service documentation
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide

## ✅ After Installation

1. **Verify** installation by opening browser to http://localhost:5000
2. **Test** login functionality
3. **Train** counselor on basic operations
4. **Provide** quick reference card to counselor
5. **Schedule** follow-up check in 24 hours

## 📞 Support

For technical issues during deployment, refer to:
- `DEPLOYMENT_CHECKLIST.md` for troubleshooting
- `SERVICE_README.md` for technical details
- Contact your IT support team

---
**Package created successfully! Ready for deployment.**