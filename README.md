# AAMUSTED Counselling Management System

A comprehensive desktop application designed for the Guidance & Counselling Centre at AAMUSTED (Akenten Appiah-Menka University of Skills Training and Entrepreneurial Development). This system provides a complete solution for managing student counselling records, appointments, session, and assessments in an offline, local environment.

## Features

### Core Functionality
- **Student Management**: Add and manage student records with complete demographic information
- **Appointment Scheduling**: Book and track counselling appointments
- **session Recording**: Document detailed counselling session with notes and interventions
- **Case Management**: Maintain comprehensive case notes and treatment plans
- **Referral System**: Track student referrals to external services
- **Assessment Tools**: Record and track DASS-21 and Outcome Questionnaire scores
- **Reporting**: Generate professional printable reports for session and case notes

### Assessment Tools
- **DASS-21 (Depression, Anxiety, Stress Scale)**: 21-item assessment with automatic scoring and interpretation
- **Outcome Questionnaire**: Standardized assessment tool for tracking client progress
- **Progress Monitoring**: Track changes over time with historical score comparisons

### User Interface
- **Intuitive Dashboard**: Quick overview of upcoming appointments, recent session, and referrals
- **Responsive Design**: Works on various screen sizes and devices
- **Professional Templates**: Clean, modern interface suitable for counselling environments
- **Print-Ready Reports**: Generate professional documents for case files and referrals

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or later
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 200MB free space for application and data
- **Display**: 1024x768 resolution or higher

### Dependencies
- Python 3.8 or later (if running from source)
- All dependencies included in the packaged .exe version

## Installation

### Option 1: Using the Packaged Application (Recommended)
1. Download the `AAMUSTED_Counseling_System.exe` file
2. Double-click to run the application
3. No additional installation required
4. The system will create a local database file in the same directory

### Option 2: Running from Source Code

#### Prerequisites
1. Install Python 3.8 or later from [python.org](https://www.python.org/downloads/)
2. Ensure Python is added to your system PATH

#### Setup Steps
```bash
# Clone or download the source code
cd AAMUSTED_Counseling_System

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Initialize the database@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file
from functools import wraps
import sqlite3
import csv
import io
import json
from datetime import datetime, timedelta
import os
from werkzeug.security import check_password_hash
from auto_report_writer import scheduler, toggle_scheduler, manual_generate_report

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}

# Add custom Jinja2 filters
def get_db_connection():
# ... rest of the filefrom flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file
from functools import wraps
import sqlite3
import csv
import io
import json
from datetime import datetime, timedelta
import os
from werkzeug.security import check_password_hash
from auto_report_writer import scheduler, toggle_scheduler, manual_generate_report

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}

# Add custom Jinja2 filters
def get_db_connection():
# ... rest of the file
python db_setup.py

# Run the application
python app.py
```

#### Access the Application
- Open your web browser
- Navigate to `http://localhost:5000`
- The system will open automatically

## Database Structure

The system uses SQLite for local data storage with the following tables:

### Core Tables
- **Students**: Student demographic information
- **Counsellors**: Staff information (pre-populated with sample data)
- **Appointments**: Counselling appointment records
- **session**: Detailed session notes and interventions
- **CaseManagement**: Comprehensive case documentation
- **Referrals**: External service referrals

### Assessment Tables
- **OutcomeQuestionnaire**: OQ-45 assessment scores
- **DASS21**: Depression, Anxiety, Stress Scale scores
- **Feedback**: Client feedback and satisfaction surveys

### Support Tables
- **Issue**: Pre-defined counselling issues (anxiety, depression, academic, etc.)
- **SessionIssue**: Many-to-many relationship between session and issues

## Usage Guide

### Getting Started
1. **First Run**: The system will automatically create the database on first run
2. **Add Students**: Use the "Add Student" form to register new students
3. **Schedule Appointments**: Book appointments through the "Appointment" form
4. **Record session**: Document session using the "session" form
5. **Manage Cases**: Create detailed case notes through "Case Note" form

### Daily Workflow
1. **Check Dashboard**: View upcoming appointments and recent activity
2. **Prepare for session**: Review student history and previous session
3. **Document session**: Complete session notes immediately after appointments
4. **Track Progress**: Use assessment tools to monitor client improvement
5. **Generate Reports**: Print professional reports for case files or referrals

### Assessment Workflow
1. **DASS-21**: Administer the 21-item questionnaire
2. **Enter Scores**: Use the DASS-21 form to input raw scores
3. **Review Results**: System automatically calculates final scores and severity levels
4. **Track Changes**: Monitor scores over time to assess progress
5. **Use for Referrals**: Use assessment results to determine need for external referrals

## Data Management

### Backup
- **Manual Backup**: Copy the `counselling.db` file to a secure location
- **Scheduled Backup**: Set up automated backup of the database file
- **Export Data**: Use SQLite tools to export data for reporting

### Data Security
- **Local Storage**: All data remains on your local machine
- **No Cloud**: No data is transmitted to external servers
- **Confidentiality**: HIPAA-compliant data handling practices
- **Access Control**: Physical security of the computer provides access control

### Data Retention
- **Automatic**: Data is retained indefinitely unless manually deleted
- **Student Records**: Maintain records as per institutional policies
- **Assessment Data**: Historical scores maintained for progress tracking

## Troubleshooting

### Common Issues

#### Database Connection Problems
- **Error**: "Database locked"
- **Solution**: Close any other applications accessing the database file

#### Port Already in Use
- **Error**: "Port 5000 already in use"
- **Solution**: Close other applications or modify `app.py` to use a different port

#### Missing Dependencies
- **Error**: "Module not found"
- **Solution**: Reinstall requirements: `pip install -r requirements.txt`

#### Print Formatting Issues
- **Problem**: Reports don't print correctly
- **Solution**: Use print preview in browser and adjust margins as needed

### Getting Help
- **Documentation**: Refer to this README for detailed instructions
- **Technical Support**: Contact the IT department for technical issues
- **Training**: Request training session for staff onboarding

## Customization

### Adding Counsellors
Edit the `db_setup.py` file to add additional counsellor names before running the database setup.

### Modifying Forms
- Templates are located in the `templates/` directory
- Forms can be customized by editing HTML files
- Database schema can be modified by updating `db_setup.py`

### Adding New Assessment Tools
1. Create new database table in `db_setup.py`
2. Add new form template in `templates/`
3. Create new route in `app.py`
4. Update navigation in `base.html`

## Privacy and Compliance

### Data Privacy
- **Local Storage**: All data remains on the local machine
- **No Tracking**: No usage analytics or data collection
- **User Control**: Complete control over data access and deletion

### HIPAA Compliance
- **Access Control**: Physical access to computer provides security
- **Audit Trail**: All session and changes are logged with timestamps
- **Data Integrity**: SQLite ensures data consistency and integrity
- **Secure Storage**: Local file system provides secure storage

## Support and Maintenance

### Regular Maintenance
- **Weekly**: Check for upcoming appointments
- **Monthly**: Review and backup database
- **Quarterly**: Update system and dependencies
- **Annually**: Review and update assessment tools

### Contact Information
- **System Administrator**: [Contact your IT department]
- **Counselling Center**: [Contact your counselling center director]
- **Technical Support**: [Contact your institutional IT support]

## License

This system is developed specifically for AAMUSTED's Guidance & Counselling Centre. All rights reserved.

## Version History

- **v1.0.0**: Initial release with core functionality
- **v1.0.1**: Added print templates and assessment tools
- **v1.0.2**: Enhanced user interface and reporting

---

**Note**: This system is designed for offline use. Ensure regular backups of your data to prevent loss.