# AAMUSTED Counselling System - Setup Guide

## Quick Start (Recommended Approach)

### Step 1: Install Dependencies
1. Run `install_dependencies.bat` as Administrator
2. This will install all required Python packages including Flask
3. Wait for installation to complete (may take 5-10 minutes)

### Step 2: Test the System
1. Run `start_manual.bat` 
2. Open your web browser and go to: http://localhost:5000
3. If the system loads, everything is working!

### Step 3: Install as Service (Optional)
If you want the system to start automatically with Windows:
1. Run `install_service.bat` as Administrator
2. The service will be installed and started automatically
3. The system will now be available at http://localhost:5000

## Troubleshooting

### If the system doesn't open:

1. **Check if Flask is installed:**
   ```
   python -c "import flask"
   ```
   If this gives an error, run `install_dependencies.bat`

2. **Test the Flask app directly:**
   ```
   python app.py
   ```
   This should start the server and show the URL http://127.0.0.1:5000

3. **Check for error messages:**
   - Look at the command window for any error messages
   - Common issues: missing dependencies, port already in use

4. **Try manual startup:**
   - Use `start_manual.bat` instead of the service
   - This gives you more visible error messages

### If the service doesn't work:

1. **Check service status:**
   ```
   sc query AAMUSTEDCounsellingService
   ```

2. **Try starting manually:**
   ```
   net start AAMUSTEDCounsellingService
   ```

3. **Check Windows Event Viewer** for service-related errors

4. **Use manual mode instead** - the service is optional

## Important Notes

- **Port 5000**: Make sure this port is not blocked by firewall
- **Administrator Rights**: Required for service installation
- **Python 3.8+**: Required for the system to work
- **Browser**: Use modern browsers (Chrome, Firefox, Edge)

## Support Files

- `install_dependencies.bat` - Installs all Python packages
- `start_manual.bat` - Starts the system manually
- `install_service.bat` - Installs as Windows service
- `test_flask.py` - Tests if Flask is working
- `windows_service.py` - Windows service implementation

## Getting Help

If you continue to have issues:
1. Run `test_flask.py` and share the output
2. Try manual startup and share any error messages
3. Check if http://localhost:5000 shows any error messages

The manual startup method (`start_manual.bat`) is often more reliable than the service method for initial testing.