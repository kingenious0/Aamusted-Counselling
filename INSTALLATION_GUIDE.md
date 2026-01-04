# AAMUSTED Counselling Management System - Installation Guide

## Quick Start (Recommended)

### For End Users (No Python Required)
1. **Download**: Get `AAMUSTED_Counseling_System.exe` from the distribution package
2. **Install**: Double-click the .exe file (no installation needed)
3. **Run**: The application will start automatically and open in your browser
4. **Use**: The system is ready for immediate use

### For Developers (Python Required)
1. **Install Python**: Download Python 3.8+ from python.org
2. **Setup**: Follow the development setup instructions below
3. **Run**: Use the provided batch file or run directly

## Detailed Installation Instructions

### Option 1: Pre-built Executable (Recommended)

#### System Requirements
- **Windows**: Windows 10 or later
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 200MB free space
- **Browser**: Any modern web browser (Chrome, Firefox, Edge, Safari)

#### Installation Steps
1. **Download the Package**
   - Get the complete distribution folder
   - Contains: `AAMUSTED_Counseling_System.exe`, README.md, Quick Start Guide

2. **Extract Files**
   - Extract to desired location (e.g., `C:\AAMUSTED_Counseling`)
   - Ensure write permissions for the folder

3. **First Run**
   - Double-click `AAMUSTED_Counseling_System.exe`
   - Database will be created automatically
   - Browser will open to `http://localhost:5000`

4. **Create Desktop Shortcut**
   - Right-click on `AAMUSTED_Counseling_System.exe`
   - Select "Send to" → "Desktop (create shortcut)"

### Option 2: Development Setup

#### Prerequisites
1. **Python Installation**
   - Download Python 3.8+ from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`

2. **Git (Optional)**
   - Download Git from https://git-scm.com/
   - Or download ZIP file from repository

#### Setup Steps

##### Step 1: Get the Code
```bash
# Option A: Git Clone
git clone [repository-url]
cd AAMUSTED_Counseling_System

# Option B: Download ZIP
# Download ZIP file and extract to desired folder
```

##### Step 2: Install Dependencies
```bash
# Navigate to project folder
cd AAMUSTED_Counseling_System

# Install required packages
pip install -r requirements.txt
```

##### Step 3: Initialize Database
```bash
# Run database setup
python db_setup.py

# This creates counselling.db with sample data
```

##### Step 4: Run the Application
```bash
# Option A: Use batch file
double-click run_system.bat

# Option B: Manual run
python app.py
```

#### Verification Steps
1. **Check Python**: `python --version` (should show 3.8+)
2. **Check Flask**: `python -c "import flask; print(flask.__version__)"`
3. **Check Database**: Ensure `counselling.db` is created
4. **Test Connection**: Visit `http://localhost:5000` in browser

## Database Setup

### Automatic Setup
- **First Run**: Database is created automatically
- **Location**: Same folder as application
- **File**: `counselling.db`
- **Backup**: Copy this file for backups

### Manual Setup (If Needed)
```bash
# Run this command to initialize database
python db_setup.py
```

### Database Location
- **Windows**: `C:\Users\[Username]\AppData\Local\AAMUSTED_Counseling_System\`
- **Portable**: Same folder as executable
- **Development**: Project root folder

## Configuration

### Port Configuration
- **Default**: Port 5000
- **Change**: Modify `app.py` line with `port=5000`
- **Check**: Use `netstat -ano` to see available ports

### Browser Settings
- **Auto-open**: Most browsers will open automatically
- **Manual**: Visit `http://localhost:5000` if browser doesn't open
- **Bookmark**: Add to bookmarks for easy access

## Troubleshooting

### Common Issues and Solutions

#### Python Not Found
**Error**: "Python was not found"
**Solution**: 
1. Install Python from python.org
2. Add Python to PATH during installation
3. Restart command prompt/computer

#### Port Already in Use
**Error**: "Address already in use"
**Solution**:
1. Close other applications using port 5000
2. Change port in `app.py`: `app.run(port=5001)`
3. Restart the application

#### Database Locked
**Error**: "Database is locked"
**Solution**:
1. Close other instances of the application
2. Wait a few seconds and retry
3. Restart the computer if persistent

#### Browser Issues
**Problem**: Browser doesn't open automatically
**Solution**:
1. Manually visit `http://localhost:5000`
2. Check firewall settings
3. Try different browser

#### Missing Dependencies
**Error**: "Module not found"
**Solution**:
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help

#### Check Logs
- **Console Output**: Look for error messages in terminal
- **Browser Console**: Press F12 → Console tab
- **System Logs**: Check Windows Event Viewer

#### Support Resources
- **README.md**: Complete documentation
- **Quick Start Guide**: Basic usage instructions
- **Technical Support**: Contact your IT department

## Security Considerations

### Data Protection
- **Local Storage**: All data stays on your computer
- **No Cloud**: No data transmitted to external servers
- **Encryption**: Database is encrypted at file system level
- **Access Control**: Physical computer access provides security

### Backup Strategy
1. **Daily**: Copy `counselling.db` file
2. **Weekly**: Full folder backup
3. **Monthly**: Archive to external storage
4. **Test**: Regularly test backup restoration

### Privacy Compliance
- **HIPAA**: Follow institutional privacy policies
- **Confidentiality**: Maintain client confidentiality
- **Access**: Limit physical access to authorized personnel
- **Audit**: Regular security reviews

## Performance Optimization

### System Requirements
- **Minimum**: 2GB RAM, 1GB free space
- **Recommended**: 4GB RAM, 2GB free space
- **Optimal**: SSD storage for faster database access

### Performance Tips
- **Close Unused Apps**: Free up system resources
- **Regular Backups**: Keep database optimized
- **System Updates**: Keep Windows updated
- **Browser Cache**: Clear browser cache periodically

## Uninstallation

### Pre-built Executable
1. **Delete**: Simply delete the executable file
2. **Database**: Optionally backup `counselling.db` first
3. **Clean**: Remove any shortcuts created

### Development Version
```bash
# Remove virtual environment
rmdir /s venv

# Delete project folder
rmdir /s AAMUSTED_Counseling_System

# Remove Python packages (optional)
pip uninstall flask
```

## Support and Contact

### Technical Support
- **Internal IT**: Contact your institutional IT department
- **Documentation**: Refer to README.md for detailed instructions
- **Updates**: Check for application updates regularly

### Training Resources
- **User Manual**: Comprehensive guide in README.md
- **Quick Reference**: Quick_Start_Guide.txt
- **Video Tutorials**: Available upon request

### Feedback and Improvements
- **Bug Reports**: Document issues with steps to reproduce
- **Feature Requests**: Submit through appropriate channels
- **Training session**: Available for staff onboarding

## Version Information
- **Current Version**: v1.0.0
- **Last Updated**: [Current Date]
- **Compatibility**: Windows 10+, Python 3.8+
- **Support**: Active development and support provided

---

**Remember**: Always backup your data before making changes to the system. The counselling database contains sensitive information that should be protected according to your institutional policies.