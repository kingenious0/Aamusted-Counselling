#!/usr/bin/env python
"""
AAMUSTED Counselling System - Windows Service
Persistent auto-start service that runs the Flask application as a Windows Service
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
import time
import threading
from datetime import datetime

# Configure logging for the service
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'counselling_service_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AAMUSTEDCounsellingService')

class AAMUSTEDCounsellingService(win32serviceutil.ServiceFramework):
    """Windows Service for AAMUSTED Counselling System"""
    
    _svc_name_ = 'AAMUSTEDCounsellingService'
    _svc_display_name_ = 'AAMUSTED Counselling System Service'
    _svc_description_ = 'Persistent auto-start service for AAMUSTED Counselling Management System. Provides continuous availability for counseling system access.'
    _svc_class_path_ = 'windows_service.AAMUSTEDCounsellingService'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
        self.flask_thread = None
        self.server = None
        
    def SvcStop(self):
        """Service stop handler"""
        logger.info('Service stop requested')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
        # Stop Flask server if running
        if self.server:
            try:
                logger.info('Shutting down Flask server...')
                self.server.shutdown()
                logger.info('Flask server shutdown complete')
            except Exception as e:
                logger.error(f'Error shutting down Flask server: {e}')
        
        # Wait for Flask thread to finish
        if self.flask_thread and self.flask_thread.is_alive():
            logger.info('Waiting for Flask thread to finish...')
            self.flask_thread.join(timeout=30)
            if self.flask_thread.is_alive():
                logger.warning('Flask thread did not stop gracefully')
        
        logger.info('Service stop complete')
        
    def SvcDoRun(self):
        """Service start handler"""
        logger.info('Service start requested')
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        
        try:
            # Change to the service directory to ensure proper paths
            service_dir = os.path.dirname(os.path.abspath(__file__))
            os.chdir(service_dir)
            logger.info(f'Service directory: {service_dir}')
            
            # Start Flask application in a separate thread
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            logger.info('Service is running')
            
            # Start Flask server
            self.start_flask_server()
            
            # Keep service running
            while self.is_running:
                # Check if Flask thread is still alive
                if self.flask_thread and not self.flask_thread.is_alive():
                    logger.error('Flask thread died unexpectedly, restarting...')
                    self.start_flask_server()
                
                # Wait for stop signal or check every 30 seconds
                rc = win32event.WaitForSingleObject(self.hWaitStop, 30000)  # 30 seconds
                if rc == win32event.WAIT_OBJECT_0:
                    break
                    
        except Exception as e:
            logger.error(f'Service error: {e}', exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_ERROR)
            raise
            
        logger.info('Service is stopping')
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        
    def start_flask_server(self):
        """Start the Flask server in a separate thread"""
        try:
            logger.info('Starting Flask server...')
            
            # Import Flask app
            from app import app
            
            # Configure Flask app for production
            app.config['DEBUG'] = False
            app.config['TESTING'] = False
            
            # Create Flask server
            from werkzeug.serving import make_server
            self.server = make_server('127.0.0.1', 5000, app, threaded=True)
            
            # Start server in a separate thread
            self.flask_thread = threading.Thread(target=self.run_flask_server, daemon=True)
            self.flask_thread.start()
            
            logger.info('Flask server started successfully on 127.0.0.1:5000')
            
        except Exception as e:
            logger.error(f'Failed to start Flask server: {e}', exc_info=True)
            raise
            
    def run_flask_server(self):
        """Run the Flask server"""
        try:
            logger.info('Flask server thread started')
            self.server.serve_forever()
        except Exception as e:
            logger.error(f'Flask server error: {e}', exc_info=True)
            if self.is_running:
                logger.info('Attempting to restart Flask server...')
                time.sleep(5)
                self.start_flask_server()

def install_service():
    """Install the Windows Service"""
    try:
        # Install the service with automatic startup
        win32serviceutil.InstallService(
            AAMUSTEDCounsellingService._svc_class_path_,
            AAMUSTEDCounsellingService._svc_name_,
            AAMUSTEDCounsellingService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START
        )
        
        # Configure service recovery options
        import win32api
        import win32con
        
        # Open service manager
        hscm = win32api.OpenSCManager(None, None, win32con.SC_MANAGER_ALL_ACCESS)
        
        # Open the service
        hs = win32api.OpenService(hscm, AAMUSTEDCounsellingService._svc_name_, win32con.SERVICE_ALL_ACCESS)
        
        # Set recovery options: restart on failure after 1 minute, up to 3 times per day
        failure_actions = [
            (win32service.SC_ACTION_RESTART, 60000),  # First failure: restart after 1 minute
            (win32service.SC_ACTION_RESTART, 60000),  # Second failure: restart after 1 minute
            (win32service.SC_ACTION_RESTART, 60000),  # Third failure: restart after 1 minute
        ]
        
        win32service.ChangeServiceConfig2(
            hs,
            win32service.SERVICE_CONFIG_FAILURE_ACTIONS,
            failure_actions,
            86400  # Reset failure count after 24 hours
        )
        
        # Close handles
        win32api.CloseServiceHandle(hs)
        win32api.CloseServiceHandle(hscm)
        
        print(f"Service '{AAMUSTEDCounsellingService._svc_display_name_}' installed successfully!")
        print("The service will start automatically on system boot.")
        print("Use 'net start AAMUSTEDCounsellingService' to start it now.")
        
    except Exception as e:
        print(f"Error installing service: {e}")
        return False
    
    return True

def uninstall_service():
    """Uninstall the Windows Service"""
    try:
        # Stop the service first
        try:
            win32serviceutil.StopService(AAMUSTEDCounsellingService._svc_name_)
            print("Service stopped successfully.")
            time.sleep(2)
        except:
            pass  # Service might not be running
            
        # Uninstall the service
        win32serviceutil.UninstallService(AAMUSTEDCounsellingService._svc_name_)
        print(f"Service '{AAMUSTEDCounsellingService._svc_display_name_}' uninstalled successfully!")
        
    except Exception as e:
        print(f"Error uninstalling service: {e}")
        return False
    
    return True

def start_service():
    """Start the Windows Service"""
    try:
        win32serviceutil.StartService(AAMUSTEDCounsellingService._svc_name_)
        print(f"Service '{AAMUSTEDCounsellingService._svc_display_name_}' started successfully!")
        return True
    except Exception as e:
        print(f"Error starting service: {e}")
        return False

def stop_service():
    """Stop the Windows Service"""
    try:
        win32serviceutil.StopService(AAMUSTEDCounsellingService._svc_name_)
        print(f"Service '{AAMUSTEDCounsellingService._svc_display_name_}' stopped successfully!")
        return True
    except Exception as e:
        print(f"Error stopping service: {e}")
        return False

def service_status():
    """Get the status of the Windows Service"""
    try:
        status = win32serviceutil.QueryServiceStatus(AAMUSTEDCounsellingService._svc_name_)
        state_map = {
            win32service.SERVICE_STOPPED: "STOPPED",
            win32service.SERVICE_START_PENDING: "STARTING",
            win32service.SERVICE_STOP_PENDING: "STOPPING",
            win32service.SERVICE_RUNNING: "RUNNING",
            win32service.SERVICE_CONTINUE_PENDING: "CONTINUING",
            win32service.SERVICE_PAUSE_PENDING: "PAUSING",
            win32service.SERVICE_PAUSED: "PAUSED"
        }
        state = state_map.get(status[1], "UNKNOWN")
        print(f"Service status: {state}")
        return state
    except Exception as e:
        print(f"Error querying service status: {e}")
        return "NOT_INSTALLED"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'install':
            install_service()
        elif sys.argv[1] == 'uninstall':
            uninstall_service()
        elif sys.argv[1] == 'start':
            start_service()
        elif sys.argv[1] == 'stop':
            stop_service()
        elif sys.argv[1] == 'status':
            service_status()
        else:
            print("Usage: python windows_service.py [install|uninstall|start|stop|status]")
            print("  install   - Install the service (requires administrator privileges)")
            print("  uninstall - Uninstall the service (requires administrator privileges)")
            print("  start     - Start the service")
            print("  stop      - Stop the service")
            print("  status    - Show service status")
    else:
        # Run as service
        win32serviceutil.HandleCommandLine(AAMUSTEDCounsellingService)