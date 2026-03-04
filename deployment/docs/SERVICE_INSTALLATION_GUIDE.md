# AAMUSTED Counselling Service Installation Guide

## Current Status
✅ **Dependencies Installed**: Flask, python-docx, APScheduler, pywin32  
✅ **Application Working**: Flask app runs successfully on port 5000  
✅ **Service Files Ready**: windows_service.py configured correctly  
❌ **Service Installation**: Requires administrator privileges  

## Installation Steps

### Step 1: Run as Administrator
1. **Close all current command windows**
2. **Right-click on Command Prompt** and select "Run as administrator"
3. **Navigate to the service directory**:
   ```cmd
   cd "C:\AAMUSTED Counselling"
   ```

### Step 2: Install the Service
Run the installation command:
```cmd
python windows_service.py install
```

### Step 3: Start the Service
After successful installation, start the service:
```cmd
net start AAMUSTEDCounsellingService
```

### Step 4: Verify Installation
Check service status:
```cmd
sc query AAMUSTEDCounsellingService
```

## Alternative: Use the Batch Script
1. **Navigate to C:\AAMUSTED Counselling** in File Explorer
2. **Right-click on** `install_service_admin.bat`
3. **Select "Run as administrator"**
4. **Follow the prompts**

## Troubleshooting

### Common Issues

1. **"Access is denied" Error**
   - Solution: Run Command Prompt as Administrator
   - Alternative: Use the batch script with admin rights

2. **Service Already Exists**
   - Uninstall first: `python windows_service.py uninstall`
   - Then reinstall with admin privileges

3. **Port 5000 Already in Use**
   - Check what's using port 5000: `netstat -ano | findstr :5000`
   - Kill the process or change the port in `windows_service.py`

4. **Service Won't Start**
   - Check Windows Event Viewer for detailed error messages
   - Verify all dependencies are installed
   - Check service logs in `C:\AAMUSTED Counselling\service_logs\`

### Verification Commands
```cmd
# Check if service is installed
sc query AAMUSTEDCounsellingService

# Check service configuration
sc qc AAMUSTEDCounsellingService

# Check if port 5000 is listening
netstat -ano | findstr :5000

# Test the application directly
python app.py
```

### Service Management Commands
```cmd
# Start service
net start AAMUSTEDCounsellingService

# Stop service
net stop AAMUSTEDCounsellingService

# Restart service
net stop AAMUSTEDCounsellingService && net start AAMUSTEDCounsellingService

# Uninstall service
python windows_service.py uninstall
```

## Next Steps After Installation
1. **Test the web interface**: Open http://localhost:5000 in your browser
2. **Verify auto-start**: Reboot the system and check if service starts automatically
3. **Test report generation**: Use the web interface to generate test reports
4. **Configure firewall**: Ensure port 5000 is accessible if needed

## Support
If you encounter issues:
1. Check the service logs in `C:\AAMUSTED Counselling\service_logs\`
2. Use the diagnostic tool: `python check_service.py`
3. Check Windows Event Viewer for service-related errors