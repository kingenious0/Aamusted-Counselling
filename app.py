from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, send_file, make_response
from functools import wraps
import sqlite3
import csv
import io
import json
from datetime import datetime, timedelta
import os
import sys
from werkzeug.security import check_password_hash, generate_password_hash
from auto_report_writer import scheduler, toggle_scheduler, manual_generate_report
import uuid
import node_config  # Import the new node config utility
from sync_engine import sync_bp, trigger_sync # Import sync engine

# Initialize Node Config on Startup
current_node_config = node_config.load_config()
print(f"--- Node Identity: {current_node_config['node_id']} ({current_node_config['node_role']}) ---")

app = Flask(__name__)
# Register Sync Blueprint
app.register_blueprint(sync_bp)

app.secret_key = 'super_secret_key_for_dev_only'  # Change for production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Global flag to prevent concurrent initialization
_db_initialization_lock = False
_db_initialized = False

def ensure_database_initialized():
    """Ensure database exists and has all required tables - atomic, single-call initialization"""
    global _db_initialization_lock, _db_initialized
    
    # If already initialized successfully, skip
    if _db_initialized:
        return
    
    # If currently initializing, wait (prevent concurrent calls)
    if _db_initialization_lock:
        import time
        wait_count = 0
        while _db_initialization_lock and wait_count < 50:  # Wait up to 5 seconds
            time.sleep(0.1)
            wait_count += 1
        if _db_initialized:
            return
    
    # Set lock to prevent concurrent initialization
    _db_initialization_lock = True
    
    try:
        # Determine database path
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
        except:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'counseling.db')
        
        # Required tables for the application
        required_tables = ['Appointment', 'Student', 'Counsellor', 'session', 'app_settings', 'Referral']
        
        # Check if database exists and has all required tables
        needs_init = False
        
        if not os.path.exists(db_path):
            print(f"[STARTUP] Database not found at: {db_path}")
            needs_init = True
        else:
            # Check for all required tables in a single connection
            try:
                check_conn = sqlite3.connect(db_path, timeout=5.0)
                cursor = check_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0].lower() for row in cursor.fetchall()}
                check_conn.close()
                
                # Check if all required tables exist (case-insensitive)
                missing_tables = []
                for req_table in required_tables:
                    if req_table.lower() not in existing_tables:
                        missing_tables.append(req_table)
                
                if missing_tables:
                    print(f"[STARTUP] Missing tables: {missing_tables}")
                    needs_init = True
                else:
                    print(f"[STARTUP] Database check passed - all required tables exist")
                    _db_initialized = True
                    _db_initialization_lock = False
                    return
            except Exception as e:
                print(f"[STARTUP] Error checking database: {e}")
                needs_init = True
        
        # Initialize database if needed (only once, atomically)
        if needs_init:
            print(f"[STARTUP] Initializing database at: {db_path}")
            try:
                # Import and run initialization (uses same path logic)
                import db_setup
                db_setup.init_db()
                
                # Verify initialization succeeded - check for Appointment table
                verify_conn = sqlite3.connect(db_path, timeout=5.0)
                verify_cursor = verify_conn.cursor()
                verify_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                verify_tables = {row[0].lower() for row in verify_cursor.fetchall()}
                verify_conn.close()
                
                # Check if all required tables now exist (case-insensitive check)
                missing_after_init = []
                for req_table in required_tables:
                    if req_table.lower() not in verify_tables:
                        missing_after_init.append(req_table)
                
                if missing_after_init:
                    print(f"[STARTUP] ERROR: Initialization incomplete! Missing tables: {missing_after_init}")
                    print(f"[STARTUP] Available tables: {verify_tables}")
                    raise Exception(f"Database initialization incomplete. Missing tables: {missing_after_init}")
                else:
                    print("[STARTUP] Database initialized successfully - all required tables verified")
                    _db_initialized = True
                    
            except Exception as e:
                print(f"[STARTUP] ERROR initializing database: {e}")
                import traceback
                traceback.print_exc()
                # Don't set _db_initialized = True so it can retry
                raise
    
    finally:
        _db_initialization_lock = False

# Initialize database when module is loaded
ensure_database_initialized()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Add custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    if value:
        return value.replace('\n', '<br>')
    return ''

# ---------- Helper Functions ----------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def get_db_connection():
    """Get database connection - works in both dev and EXE mode"""
    # Ensure database is initialized first (only once)
    ensure_database_initialized()
    
    # Get database path
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(base_path, 'counseling.db')
    
    # Connect with timeout to prevent locking issues
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    
    # Quick verification that Student table exists (most critical table)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='Student' OR name='student')")
        if not cursor.fetchone():
            print("[GET_DB_CONNECTION] Student table missing! Reinitializing...")
            conn.close()
            # Force reinitialization
            global _db_initialized
            _db_initialized = False
            ensure_database_initialized()
            # Reconnect
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
    except Exception as verify_error:
        print(f"[GET_DB_CONNECTION] Error verifying tables: {verify_error}")
        # Continue anyway - let the query fail and be caught by route handlers
    
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('welcome'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_node_info():
    """Inject node info into all templates"""
    return dict(node_config=node_config.load_config())

@app.route('/admin/settings/node', methods=['POST'])
@login_required
def update_node_settings():
    if session.get('role') != 'Admin':
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        new_role = request.form.get('node_role')
        peer_ip = request.form.get('peer_ip')
        
        config = node_config.load_config()
        config['node_role'] = new_role
        config['peer_ip'] = peer_ip
        node_config.save_config(config)
        
        flash('Node settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
        
    return redirect(url_for('admin_settings'))

@app.route('/admin/sync/now')
@login_required
def manual_sync():
    """Manual trigger for sync"""
    # Only Admin or authorized roles should trigger sync manually, but safe for now
    result = trigger_sync()
    if result.get('status') == 'success':
        flash(f"Sync completed. {result.get('message', '')}", 'success')
    else:
        flash(f"Sync failed: {result.get('message')}", 'error')
    return redirect(url_for('admin_settings'))

@app.context_processor
def inject_notifications():
    if not session.get('logged_in'):
        return {}
    
    try:
        user_id = session.get('user_id')
        conn = get_db_connection()
        # Fetch unread notifications
        notifs = conn.execute('''
            SELECT * FROM Notification 
            WHERE user_id = ? AND is_read = 0 
            ORDER BY created_at DESC LIMIT 5
        ''', (user_id,)).fetchall()
        
        unread_count = conn.execute('''
            SELECT COUNT(*) FROM Notification 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,)).fetchone()[0]
        
        conn.close()
        return {'notifications': notifs, 'unread_count': unread_count}
    except:
        return {'notifications': [], 'unread_count': 0}

@app.context_processor
def inject_settings():
    try:
        conn = get_db_connection()
        settings_rows = conn.execute("SELECT setting_name, setting_value FROM app_settings").fetchall()
        conn.close()
        settings = {row['setting_name']: row['setting_value'] for row in settings_rows}
        return {'settings': settings}
    except:
        return {'settings': {}}

@app.route('/audit_logs')
@login_required
def audit_logs():
    if session.get('role') != 'Admin':
        flash("Unauthorized access to audit trails.", "error")
        return redirect(url_for('dashboard'))
    
    try:
        conn = get_db_connection()
        logs = conn.execute('''
            SELECT al.*, u.username, u.full_name 
            FROM audit_logs al 
            JOIN users u ON al.user_id = u.id 
            ORDER BY al.created_at DESC LIMIT 100
        ''').fetchall()
        conn.close()
        return render_template('audit_logs.html', logs=logs)
    except Exception as e:
        flash(f"Error loading logs: {e}", "error")
        return redirect(url_for('dashboard'))
        return render_template('audit_logs.html', logs=logs)
    except Exception as e:
        flash(f"Error loading logs: {e}", "error")
        return redirect(url_for('dashboard'))

# ---------- NOTIFICATION SYSTEM ----------
@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        conn = get_db_connection()
        user_id = session.get('user_id')
        # Only allow user to mark their own notifications
        conn.execute("UPDATE Notification SET is_read = 1 WHERE id = ? AND user_id = ?", (notification_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"[NOTIFICATION] Error marking read: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/notifications/mark_all_read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    try:
        conn = get_db_connection()
        user_id = session.get('user_id')
        conn.execute("UPDATE Notification SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"[NOTIFICATION] Error marking all read: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def create_notification(user_id, message, link=None, type='in_app', sender_info=None):
    """Create a notification for a user."""
    try:
        conn = get_db_connection()
        
        # Append sender info if provided and accessible
        final_message = message
        if sender_info:
             final_message = f"{message} (Sent by {sender_info})"
        elif session and session.get('role'):
             # If we are in a request context with a session
             try:
                 sender_role = session.get('role')
                 if sender_role:
                    final_message = f"{message} (Sent by {sender_role})"
             except:
                 pass
             
        conn.execute(
            "INSERT INTO Notification (user_id, message, link, type) VALUES (?, ?, ?, ?)",
            (user_id, final_message, link, type)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[NOTIFICATION] Error: {e}")

def notify_role(role, message, link=None):
    """Notify all users with a specific role."""
    try:
        conn = get_db_connection()
        # Case insensitive role matching
        users = conn.execute(
            "SELECT id FROM users WHERE LOWER(role) = LOWER(?)", 
            (role,)
        ).fetchall()
        
        sender_info = None
        try:
            if session:
                sender_info = session.get('role')
        except:
            pass

        for user in users:
            create_notification(user['id'], message, link, sender_info=sender_info)
        conn.close()
    except Exception as e:
        print(f"[NOTIFICATION_BROADCAST] Error: {e}")
# ---------- Routes ----------
@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('welcome'))

@app.route('/welcome', methods=['GET'])
def welcome():
    try:
        # Check if user is already logged in - if so, redirect to dashboard
        if session.get('logged_in'):
            # Check if already visited today
            last_visit_date = session.get('last_visit_date')
            today = datetime.now().date().isoformat()
            
            # If already visited today, go to dashboard
            if last_visit_date == today:
                return redirect(url_for('dashboard'))
        
        # Ensure database is initialized before showing welcome page
        try:
            ensure_database_initialized()
        except Exception as e:
            print(f"[WELCOME] Database init error: {e}")
            # Still show welcome page, but log the error
        
        # Show welcome screen (for login page)
        return render_template('welcome.html')
    except Exception as e:
        print(f"[WELCOME] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return f'''
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error Loading Welcome Page</h1>
            <p>An error occurred: {str(e)}</p>
            <p>Check error_log.txt in the application folder for details.</p>
        </body>
        </html>
        ''', 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        # Ensure database is initialized before connection
        try:
            ensure_database_initialized()
        except Exception as db_init_error:
            print(f"[LOGIN] Database init error: {db_init_error}")
            flash('Database initialization error. Please restart the application.', 'error')
            return redirect(url_for('welcome'))
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('welcome'))
        
        user = None
        try:
            # Check user against the users table
            user = conn.execute(
                "SELECT * FROM users WHERE LOWER(username) = ?", (username,)
            ).fetchone()
        except Exception as db_error:
            print(f"[LOGIN] Database query error: {db_error}")
            # Try once to see if users table is missing
            if 'no such table' in str(db_error).lower():
                print("[LOGIN] Users table missing, reinitializing database...")
                conn.close()
                ensure_database_initialized()
                conn = get_db_connection()
                user = conn.execute("SELECT * FROM users WHERE LOWER(username) = ?", (username,)).fetchone()
            else:
                flash('Database error. Please restart the application.', 'error')
                return redirect(url_for('welcome'))
        finally:
            try:
                conn.close()
            except:
                pass
    except Exception as e:
        print(f"[LOGIN] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Login error: {str(e)}', 'error')
        return redirect(url_for('welcome'))

    if user and check_password_hash(user['password_hash'], password):
        # Professional standard: store essential info in session
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        session.permanent = True
        
        # Track visit for daily greeting
        today = datetime.now().date().isoformat()
        last_visit = session.get('last_visit_date')
        session['first_visit_today'] = (last_visit != today)
        session['last_visit_date'] = today
        
        # Log the login in audit_logs
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO audit_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
                (user['id'], 'LOGIN', f"User logged in successfully", request.remote_addr)
            )
            conn.commit()
            conn.close()
        except Exception as log_error:
            print(f"[LOGIN] Audit log error: {log_error}")
            
        print(f"[LOGIN] Success: {username} logged in as {user['role']}")
        return redirect(url_for('dashboard'))
    else:
        print(f"[LOGIN] Failed attempt for username: {username}")
        flash('Invalid username or password.', 'error')
    
    return redirect(url_for('welcome'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user_role = session.get('role', 'Counsellor')
        user_name = session.get('full_name', 'Counsellor')
        
        # Check if this is first visit today
        show_welcome_message = session.pop('first_visit_today', False)
        
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('welcome'))
        
        # Initialize variables with defaults
        stats = {
            'total_students': 0,
            'today_count': 0,
            'total_sessions': 0,
            'sent_to_counsellor': 0,
            'in_session': 0
        }
        today_appts = []
        pending_action = []  # Role-specific workload
        recent_activity = []
        
        # 1. Get GLOBAL stats for dashboard counters
        try:
            stats['total_students'] = conn.execute('SELECT COUNT(*) FROM Student').fetchone()[0]
            stats['today_count'] = conn.execute("SELECT COUNT(*) FROM Appointment WHERE date = DATE('now')").fetchone()[0]
            stats['total_sessions'] = conn.execute('SELECT COUNT(*) FROM session').fetchone()[0]
            stats['total_users'] = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            
            # Workflow specific stats for the counters
            stats['sent_to_counsellor'] = conn.execute("SELECT COUNT(*) FROM Appointment WHERE status = 'Sent to Counsellor'").fetchone()[0]
            stats['in_session'] = conn.execute("SELECT COUNT(*) FROM Appointment WHERE status = 'In Session'").fetchone()[0]
        except Exception as e:
            print(f"[DASHBOARD] Stats error: {e}")

        # 2. Define Workload based on Role
        if user_role == 'Secretary' or user_role == 'Admin':
            try:
                # Cases awaiting handover (Secretary's queue) - Show ALL scheduled items
                pending_action = conn.execute('''
                    SELECT a.*, s.name as student_name 
                    FROM Appointment a JOIN Student s ON a.student_id = s.id 
                    WHERE a.status = 'Scheduled'
                    ORDER BY a.date ASC, a.time ASC
                ''').fetchall()
                
                # Recently sent activity
                recent_activity = conn.execute('''
                    SELECT a.*, s.name as student_name 
                    FROM Appointment a JOIN Student s ON a.student_id = s.id 
                    WHERE a.status = 'Sent to Counsellor'
                    ORDER BY a.created_at DESC LIMIT 5
                ''').fetchall()
            except Exception as e:
                print(f"[DASHBOARD] Workload query error: {e}")
        
        elif user_role == 'Counsellor':
            try:
                # Incoming Case Referrals (Counsellor's queue)
                pending_action = conn.execute('''
                    SELECT a.*, s.name as student_name 
                    FROM Appointment a JOIN Student s ON a.student_id = s.id 
                    WHERE a.status = 'Sent to Counsellor' OR a.status = 'Checked In'
                    ORDER BY a.date ASC, a.time ASC
                ''').fetchall()
                
                # Active Sessions for the current Counsellor
                today_appts = conn.execute('''
                    SELECT a.*, s.name as student_name 
                    FROM Appointment a JOIN Student s ON a.student_id = s.id 
                    WHERE a.status = 'In Session'
                    ORDER BY a.time ASC
                ''').fetchall()
            except Exception as e:
                print(f"[DASHBOARD] Counsellor query error: {e}")

        # Generate greeting
        current_hour = datetime.now().hour
        if current_hour < 12:
            time_greeting = "Good morning"
        elif current_hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        greeting = f"{time_greeting}, {user_name}"
        if show_welcome_message:
            greeting += " - Welcome Back! 👋"

        # Ensure connection is closed before rendering
        try:
            conn.close()
        except:
            pass

        # Pass all template variables
        if user_role == 'Admin':
            return render_template('admin_dashboard.html', 
                                stats=stats, 
                                greeting=greeting, 
                                pending_action=pending_action,
                                recent_activity=recent_activity,
                                show_welcome_message=show_welcome_message)
        else:
            # SWITCH TO MODERN DASHBOARD
            return render_template('dashboard_modern.html', 
                                role=user_role,
                                greeting=greeting,
                                stats=stats,
                                today_appts=today_appts,
                                pending_action=pending_action,
                                recent_activity=recent_activity,
                                show_welcome_message=show_welcome_message)
                             
    except Exception as e:
        print(f"[DASHBOARD] Critical error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('welcome'))

@app.route('/appointment/update_status/<int:appt_id>/<new_status>')
@login_required
def update_appt_status(appt_id, new_status):
    # Standardize Status Input
    status_map = {
        'scheduled': 'Scheduled',
        'checked_in': 'Checked In',
        'sent_to_counsellor': 'Sent to Counsellor',
        'accepted': 'Accepted', # Intermediate state
        'in_session': 'In Session',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    
    clean_status = status_map.get(new_status.lower().replace(' ', '_'), new_status)
    
    user_role = session.get('role')
    conn = get_db_connection()
    
    # Get current status
    appt = conn.execute("SELECT status, student_id FROM Appointment WHERE id = ?", (appt_id,)).fetchone()
    if not appt:
        conn.close()
        flash("Appointment not found.", "error")
        return redirect(url_for('dashboard'))
        
    current_status = appt['status']
    student_name = conn.execute("SELECT name FROM Student WHERE id = ?", (appt['student_id'],)).fetchone()['name']

    # --- STRICT WORKFLOW ENGINE ---
    allowed = False
    error_msg = "Invalid workflow transition."
    
    # 1. Secretary: Scheduled -> Checked In (Step 1)
    if current_status == 'Scheduled' and clean_status == 'Checked In':
        if user_role in ['Secretary', 'Admin']:
            allowed = True
        else:
            error_msg = "Only Secretary can check in students."

    # 1.5. Secretary: Scheduled -> Sent to Counsellor (Direct Handover)
    elif current_status == 'Scheduled' and clean_status == 'Sent to Counsellor':
        if user_role in ['Secretary', 'Admin']:
            allowed = True
            # Notify Counsellors
            notify_role('Counsellor', f"Incoming Patient: {student_name}", url_for('dashboard'))
            notify_role('Counselor', f"Incoming Patient: {student_name}", url_for('dashboard'))
        else:
             error_msg = "Only Secretary can handover students."

    # 2. Secretary: Checked In -> Sent to Counsellor (Step 2)
    elif current_status == 'Checked In' and clean_status == 'Sent to Counsellor':
        if user_role in ['Secretary', 'Admin']:
            allowed = True
            notify_role('Counsellor', f"Incoming Patient: {student_name}", url_for('dashboard'))
            notify_role('Counselor', f"Incoming Patient: {student_name}", url_for('dashboard'))
        else:
            error_msg = "Only Secretary can handover students."

    # 3. Counsellor: Sent to Counsellor -> In Session
    elif (current_status == 'Sent to Counsellor' or current_status == 'Checked In') and clean_status == 'In Session':
        if user_role in ['Counsellor', 'Counselor', 'Admin']:
            allowed = True
        else:
             error_msg = "Only Counsellor can start a session."

    # 4. Counsellor: In Session -> Completed
    elif current_status == 'In Session' and clean_status == 'Completed':
        if user_role in ['Counsellor', 'Counselor', 'Admin']:
            allowed = True
        else:
             error_msg = "Only Counsellor can complete a session."

    # 4.5. Counsellor: Completed -> In Session (Re-open case)
    elif current_status == 'Completed' and clean_status == 'In Session':
        if user_role in ['Counsellor', 'Counselor', 'Admin']:
            allowed = True
        else:
             error_msg = "Only Counsellor can re-open a session."
             
    # 5. Anyone: -> Scheduled (Send Back/Reset)
    elif clean_status == 'Scheduled':
         allowed = True # Allow reset

    if not allowed:
        conn.close()
        flash(f"Workflow Error: {error_msg} ({current_status} -> {clean_status})", "error")
        return redirect(url_for('dashboard'))

    # Update DB
    try:
        # Update status and timestamps
        timestamp_col = None
        if clean_status == 'Checked In': timestamp_col = 'checked_in_at'
        if clean_status == 'Sent to Counsellor': timestamp_col = 'sent_to_counsellor_at'
        if clean_status == 'In Session': timestamp_col = 'accepted_at'
        if clean_status == 'Completed': timestamp_col = 'completed_at'
        
        sql = "UPDATE Appointment SET status = ?"
        params = [clean_status]
        
        if timestamp_col:
            sql += f", {timestamp_col} = CURRENT_TIMESTAMP"
        
        # If jumping from Scheduled to Sent to Counsellor, ensure checked_in_at is also set if null
        if current_status == 'Scheduled' and clean_status == 'Sent to Counsellor':
            sql += ", checked_in_at = COALESCE(checked_in_at, CURRENT_TIMESTAMP)"
            
        sql += " WHERE id = ?"
        params.append(appt_id)
        
        conn.execute(sql, params)
        
        conn.execute(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
            (session.get('user_id'), 'WORKFLOW', f"Moved {student_name} from {current_status} to {clean_status}")
        )
        conn.commit()
        conn.close()
        
        # Success Feedback
        flash(f"Moved {student_name} to {clean_status}", "success")
        
        # If starting a session, redirect to the session notes page
        if clean_status == 'In Session':
            return redirect(url_for('create_session', appointment_id=appt_id))
            
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"[WORKFLOW] Error updating status: {e}")
        conn.close()
        flash(f"Database Error: {str(e)}", "error")
        
    return redirect(url_for('dashboard'))

# ---------- ADMIN USER MANAGEMENT ----------

@app.route('/admin/users')
@login_required
def admin_users():
    if session.get('role') != 'Admin':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash('All fields are required', 'error')
            return redirect(url_for('admin_add_user'))
            
        hashed_pw = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
                        (username, hashed_pw, full_name, role))
            conn.execute('INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)',
                        (session.get('user_id'), 'USER_CREATE', f"Created user {username} ({role})"))
            conn.commit()
            conn.close()
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('admin_users'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
            
    return render_template('admin_add_user.html')

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
        
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
        
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.execute('INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)',
                    (session.get('user_id'), 'USER_DELETE', f"Deleted user ID {user_id}"))
        conn.commit()
        conn.close()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'error')
        
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reset_password', methods=['POST'])
@login_required
def admin_reset_password():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
        
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    if not user_id or not new_password:
        flash('Missing data for password reset.', 'error')
        return redirect(url_for('admin_users'))
        
    try:
        hashed_pw = generate_password_hash(new_password)
        conn = get_db_connection()
        conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_pw, user_id))
        conn.execute('INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)',
                    (session.get('user_id'), 'USER_PW_RESET', f"Reset password for user ID {user_id}"))
        conn.commit()
        conn.close()
        flash('Password reset successfully.', 'success')
    except Exception as e:
        flash(f'Error resetting password: {e}', 'error')
        
    return redirect(url_for('admin_users'))

@app.route('/admin/workflow')
@login_required
def admin_workflow():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    # Fetch settings or set defaults
    auto_notify = conn.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'workflow_auto_notify'").fetchone()
    lock_notes = conn.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'workflow_lock_notes'").fetchone()
    conn.close()
    
    settings = {
        'auto_notify': auto_notify['setting_value'] == 'true' if auto_notify else True,
        'lock_notes': lock_notes['setting_value'] == 'true' if lock_notes else True
    }
    
    return render_template('admin_workflow.html', settings=settings)

@app.route('/admin/settings')
@login_required
def admin_settings():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    # Fetch all settings
    settings_rows = conn.execute("SELECT setting_name, setting_value FROM app_settings").fetchall()
    conn.close()
    
    # Convert list of rows to dictionary
    settings = {row['setting_name']: row['setting_value'] for row in settings_rows}
    
    return render_template('admin_settings.html', settings=settings)

@app.route('/admin/settings/update', methods=['POST'])
@login_required
def admin_update_settings():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
        
    try:
        conn = get_db_connection()
        
        # List of settings to update
        setting_keys = ['system_name', 'logo_url', 'theme_color']
        
        for key in setting_keys:
            val = request.form.get(key)
            if val is not None:
                # Upsert logic (SQLite specific or simple delete/insert)
                # Since we don't know if key exists, we can do REPLACE INTO or checking first.
                # Simplest for SQLite: INSERT OR REPLACE if primary key is set, but we don't have PK on name maybe?
                # Let's check schema. Assuming key-value pair uniqueness is enforced or not,
                # let's try to update, if 0 rows, insert.
                
                cursor = conn.cursor()
                cursor.execute("UPDATE app_settings SET setting_value = ? WHERE setting_name = ?", (val, key))
                if cursor.rowcount == 0:
                    cursor.execute("INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)", (key, val))
                    
        conn.commit()
        conn.close()
        flash("System configuration updated successfully.", "success")
    except Exception as e:
        flash(f"Error saving settings: {e}", "error")
        
    return redirect(url_for('admin_settings'))

@app.route('/admin/workflow/save', methods=['POST'])
@login_required
def save_workflow_settings():
    if session.get('role') != 'Admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.get_json()
        conn = get_db_connection()
        
        # Upsert logic (delete then insert is easier for simple KV)
        conn.execute("DELETE FROM app_settings WHERE setting_name IN ('workflow_auto_notify', 'workflow_lock_notes')")
        
        conn.execute("INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)", 
                     ('workflow_auto_notify', 'true' if data.get('auto_notify') else 'false'))
        conn.execute("INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)", 
                     ('workflow_lock_notes', 'true' if data.get('lock_notes') else 'false'))
                     
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/forms')
@login_required
def admin_forms():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))
    return render_template('admin_forms.html')

@app.route('/admin/export/master')
@login_required

def admin_export_master():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard'))

    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Font, PatternFill
        import io
    except ImportError:
        flash("Export library missing. Please contact support.", "error")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    
    # 1. Fetch Datasets
    students = conn.execute("SELECT * FROM Student").fetchall()
    appointments = conn.execute("SELECT * FROM Appointment").fetchall()
    intake_forms = conn.execute("SELECT * FROM intake_forms").fetchall()
    users = conn.execute("SELECT id, username, full_name, role, last_login, created_at FROM users").fetchall()
    
    conn.close()

    # 2. Create Workbook
    wb = openpyxl.Workbook()
    
    # Helper to write sheet
    def write_sheet(wb, sheet_name, data, columns=None):
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.create_sheet(sheet_name)
            
        if not data:
            ws.append(["No Data Available"])
            return

        # Headers
        if not columns:
            columns = data[0].keys()
        
        # Style headers
        header_font = Font(bold=True, color="FFFFFFFF")
        header_fill = PatternFill(start_color="FF4F81BD", end_color="FF4F81BD", fill_type="solid")
        
        for col_num, col_title in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_num, value=str(col_title).upper())
            cell.font = header_font
            cell.fill = header_fill

        # Data
        for row_data in data:
            row_values = [row_data[col] for col in columns]
            ws.append(row_values)
            
        # Autosize columns
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = min(adjusted_width, 50)

    # 3. Populate Sheets
    # Remove default sheet
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']
        
    write_sheet(wb, "Students", students)
    write_sheet(wb, "Appointments", appointments)
    write_sheet(wb, "Intake Records", intake_forms)
    write_sheet(wb, "System Users", users)

    # 4. Return File
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=Master_Data_Export_{timestamp}.xlsx'
    return response

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('welcome'))

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('students'))

        if request.method == 'POST':
            edit_id = request.form.get('edit_id')

            name = request.form.get('name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            index_number = request.form.get('index_number')
            department = request.form.get('department')
            programme = request.form.get('programme')
            contact = request.form.get('contact')
            parent_contact = request.form.get('parent_contact')
            hall_of_residence = request.form.get('hall_of_residence')
            faculty = request.form.get('faculty', '')

            try:
                if edit_id:
                    conn.execute('''
                        UPDATE Student 
                        SET name=?, age=?, gender=?, index_number=?, department=?, faculty=?, 
                            programme=?, contact=?, parent_contact=?, hall_of_residence=?
                        WHERE id=?
                    ''', (name, age if age else None, gender, index_number, department, faculty, 
                          programme, contact, parent_contact, hall_of_residence, edit_id))
                    flash('Student updated successfully!', 'success')
                else:
                    conn.execute(
                        'INSERT INTO Student (name, age, gender, index_number, department, faculty, programme, contact, parent_contact, hall_of_residence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (name, age if age else None, gender, index_number, department, faculty, programme, contact, parent_contact, hall_of_residence)
                    )
                    flash('Student added successfully!', 'success')
                conn.commit()
                return redirect(url_for('students'))
            except sqlite3.IntegrityError:
                conn.rollback()
                flash('Error: Index number already exists.', 'error')
                if edit_id:
                    try:
                        student = conn.execute('SELECT * FROM Student WHERE id = ?', (edit_id,)).fetchone()
                        return render_template('add_student.html', student=student)
                    except Exception:
                        pass
            except Exception as e:
                conn.rollback()
                print(f"[ADD_STUDENT] Error saving student: {e}")
                import traceback
                traceback.print_exc()
                # Check if it's a table missing error and reinitialize
                if 'no such table' in str(e).lower() or 'Student' in str(e):
                    print("[ADD_STUDENT] Table missing error detected, reinitializing database...")
                    try:
                        ensure_database_initialized()
                        conn = get_db_connection()
                        flash('Database was reinitialized. Please try again.', 'info')
                    except Exception as init_error:
                        print(f"[ADD_STUDENT] Error reinitializing: {init_error}")
                        flash(f'Database error: {str(e)}. Please restart the application.', 'error')
                else:
                    flash(f'Error saving student: {str(e)}', 'error')
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        else:
            student = None
            edit_id = request.args.get('edit')
            if edit_id:
                try:
                    student = conn.execute('SELECT * FROM Student WHERE id = ?', (edit_id,)).fetchone()
                except Exception as e:
                    print(f"[ADD_STUDENT] Error loading student for edit: {e}")
                    import traceback
                    traceback.print_exc()
                    # Check if it's a table missing error and reinitialize
                    if 'no such table' in str(e).lower() or 'Student' in str(e):
                        print("[ADD_STUDENT] Table missing error detected in GET, reinitializing database...")
                        try:
                            ensure_database_initialized()
                            conn = get_db_connection()
                            student = conn.execute('SELECT * FROM Student WHERE id = ?', (edit_id,)).fetchone()
                        except Exception as init_error:
                            print(f"[ADD_STUDENT] Error reinitializing: {init_error}")
                            student = None
                    else:
                        student = None
            try:
                conn.close()
            except Exception:
                pass
            return render_template('add_student.html', student=student, user_name=session.get('full_name'))

    except Exception as e:
        print(f"[ADD_STUDENT] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading student form. Please try again.', 'error')
        return redirect(url_for('students'))


@app.route('/sessions')
@login_required
def sessions_list():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        sessions_raw = []
        try:
            # Get sessions with full details including student, counsellor, and appointment info
            sessions_raw = conn.execute('''
                SELECT sess.id, sess.session_type, sess.notes, sess.created_at,
                       s.id as student_db_id, s.name as student_name,
                       c.name as Counsellor_name,
                       a.date, a.time, a.status,
                       sess.appointment_id
                FROM session sess
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                ORDER BY sess.created_at DESC
            ''').fetchall()
        except Exception as e:
            print(f"[SESSIONS] Error getting sessions: {e}")
            sessions_raw = []
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        # Convert to list and add professional IDs
        sessions = []
        for sess in sessions_raw:
            sess_dict = dict(sess)
            student_db_id = sess_dict.get('student_db_id', 0)
            sess_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
            sessions.append(sess_dict)
        
        # Create a simple pagination object to prevent template errors
        class SimplePagination:
            has_prev = False
            has_next = False
            page = 1
            prev_num = None
            next_num = None
            def iter_pages(self):
                return []
        
        pagination = SimplePagination()
        return render_template('sessions.html', sessions=sessions, pagination=pagination)
    except Exception as e:
        print(f"[SESSIONS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading sessions. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/create_session', methods=['GET', 'POST'])
@login_required
def create_session():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            appointment_id = request.form.get('appointment_id')
            session_type = request.form.get('session_type')
            notes = request.form.get('notes')
            outcome = request.form.get('outcome', '')

            try:
                # Get appointment details
                appointment = conn.execute('''
                    SELECT student_id, status 
                    FROM Appointment 
                    WHERE id = ?
                ''', (appointment_id,)).fetchone()

                if appointment:
                    student_id = appointment['student_id']
                    appointment_status = appointment['status']

                    # Insert new session - use appointment_id as the foreign key
                    conn.execute('''
                        INSERT INTO session (appointment_id, session_type, notes, outcome, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (appointment_id, session_type, notes, outcome, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                    # Update appointment status to completed only if it's currently scheduled
                    if appointment_status == 'scheduled':
                        conn.execute('UPDATE Appointment SET status = ? WHERE id = ?', 
                                     ('Completed', appointment_id))

                    conn.commit()
                    flash('Session created successfully!')
                    
                    # Check for follow-up scheduling
                    if request.form.get('schedule_followup'):
                         return redirect(url_for('appointment', student_id=student_id))
                         
                    return redirect(url_for('sessions_list'))
                else:
                    flash('Invalid appointment selected.')
                    return redirect(url_for('create_session'))
            except Exception as e:
                conn.rollback()
                print(f"[CREATE_SESSION] Error creating session: {e}")
                flash(f'Error creating session: {str(e)}', 'error')
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
            return redirect(url_for('create_session'))

        # GET: load appointments for dropdown and potential context
        appointments = []
        try:
            appointments = conn.execute('''
                SELECT a.id, a.date as date, a.time as time, a.status, s.name as student_name,
                       c.name as counsellor_name, a.urgency, a.referral_source, a.purpose
                FROM Appointment a
                LEFT JOIN Student s ON a.student_id = s.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                WHERE a.status IN ('scheduled', 'Scheduled', 'In Session', 'Completed', 'completed', 'Sent to Counsellor')
                ORDER BY a.date DESC, a.time DESC
            ''').fetchall()
        except Exception as e:
            print(f"[CREATE_SESSION] Error getting appointments: {e}")
            appointments = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Check if specific appointment_id is passed in args (from Dashboard or Queue)
        selected_appt_id = request.args.get('appointment_id')
        return render_template('create_session.html', appointments=appointments, selected_appt_id=selected_appt_id)
    except Exception as e:
        print(f"[CREATE_SESSION] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading session creation page. Please try again.', 'error')
        return redirect(url_for('dashboard'))
@app.route('/case_note', methods=['GET', 'POST'])
@login_required
def case_note():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            session_id = request.form.get('session_id')
            client_appearance = request.form.get('client_appearance', '')
            problems = request.form.get('problems', '')
            interventions = request.form.get('interventions', '')
            recommendations = request.form.get('recommendations', '')
            next_visit_date = request.form.get('next_visit_date') or None
            counsellor_signature = request.form.get('counsellor_signature', '')

            # Validate required fields
            if not session_id:
                flash('Please select a session', 'error')
                return redirect(url_for('case_note'))
            
            if not all([client_appearance, problems, interventions, recommendations]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('case_note'))

            try:
                # Check if case management record already exists for this session
                existing = conn.execute('SELECT id FROM CaseManagement WHERE session_id = ?', (session_id,)).fetchone()
                
                if existing:
                    # Update existing record
                    conn.execute('''
                        UPDATE CaseManagement 
                        SET client_appearance = ?, problems = ?, interventions = ?, recommendations = ?,
                            next_visit_date = ?, counsellor_signature = ?
                        WHERE session_id = ?
                    ''', (client_appearance, problems, interventions, recommendations, 
                          next_visit_date, counsellor_signature, session_id))
                else:
                    # Insert new record
                    conn.execute('''
                        INSERT INTO CaseManagement 
                        (session_id, client_appearance, problems, interventions, recommendations, 
                         next_visit_date, counsellor_signature, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (session_id, client_appearance, problems, interventions, recommendations,
                          next_visit_date, counsellor_signature, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                conn.commit()
                flash('Case notes saved successfully!', 'success')
                return redirect(url_for('sessions_list'))
            except Exception as e:
                conn.rollback()
                print(f"[CASE_NOTE] Error saving case notes: {e}")
                import traceback
                traceback.print_exc()
                flash(f'Error saving case notes: {str(e)}', 'error')
                return redirect(url_for('case_note'))
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        # GET request - show form
        sessions = []
        try:
            sessions_raw = conn.execute('''
                SELECT s.id, st.id as student_db_id, st.name as student_name, s.created_at
                FROM session s
                JOIN Appointment a ON s.appointment_id = a.id
                JOIN Student st ON a.student_id = st.id
                ORDER BY s.created_at DESC
            ''').fetchall()
            # Convert to list and add professional IDs
            sessions = []
            for sess in sessions_raw:
                sess_dict = dict(sess)
                student_db_id = sess_dict.get('student_db_id', 0)
                sess_dict['professional_id'] = f"C{student_db_id:03d}"
                sessions.append(sess_dict)
        except Exception as e:
            print(f"[CASE_NOTE] Error getting sessions: {e}")
            sessions = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return render_template('case_note.html', sessions=sessions, now=datetime.utcnow())
    except Exception as e:
        print(f"[CASE_NOTE] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading case notes page. Please try again.', 'error')
        return redirect(url_for('dashboard'))

# ---------- Reports Routes ----------
@app.route('/reports')
@login_required
def reports_list():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        reports = []
        try:
            # Get all generated reports from the database
            reports = conn.execute('''
                SELECT id, title, date_generated, report_type, summary, file_path
                FROM reports
                ORDER BY date_generated DESC
            ''').fetchall()
        except Exception as e:
            print(f"[REPORTS] Error getting reports: {e}")
            reports = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return render_template('reports.html', reports=reports)
    except Exception as e:
        print(f"[REPORTS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading reports. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/generate_report_manual', methods=['POST'], endpoint='generate_report_manual')
@login_required
def generate_report_manual():
    """Generate a report manually with custom options"""
    report_type = request.form.get('report_type', 'manual')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    try:
        if report_type == 'custom' and start_date and end_date:
            # Custom date range - modify the generate_report function to accept dates
            manual_generate_report()  # For now, use manual generation
            flash('Custom report generation is being prepared. Report generated successfully!', 'success')
        else:
            manual_generate_report()
            flash('Report generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
    
    return redirect(url_for('reports_list'))

@app.route('/toggle_auto_report', methods=['GET', 'POST'])
@login_required
def toggle_auto_report():
    """Toggle auto report generation on/off"""
    if request.method == 'POST':
        data = request.get_json()
        enable = data.get('enable', False)
        
        try:
            toggle_scheduler(enable)
            return jsonify({
                'status': 'success',
                'message': f'Auto report generation {"enabled" if enable else "disabled"} successfully.',
                'is_enabled': enable
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    else:
        # GET request - return current status
        is_running = scheduler.running if scheduler else False
        return jsonify({
            'status': 'success',
            'is_enabled': is_running
        })

@app.route('/generate_report_now', methods=['POST'])
@login_required
def generate_report_now():
    """Manually trigger report generation"""
    try:
        manual_generate_report()
        return jsonify({
            'status': 'success',
            'message': 'Report generated successfully! Check the Reports page to view it.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating report: {str(e)}'
        }), 500
@app.route('/my_cases')
@login_required
def my_cases():
    # Only for Clinical roles
    if session.get('role') not in ['Counsellor', 'Counselor', 'Admin']:
        flash("Access restricted to clinical staff.", "error")
        return redirect(url_for('dashboard'))
        
    try:
        conn = get_db_connection()
        user_full_name = session.get('full_name')
        
        # 1. Find Counsellor ID based on User Name
        counsellor = conn.execute("SELECT id FROM Counsellor WHERE name = ?", (user_full_name,)).fetchone()
        
        if not counsellor:
            # Fallback for Admin - show all
            if session.get('role') == 'Admin':
                 students = conn.execute("SELECT * FROM Student ORDER BY name").fetchall()
                 conn.close()
                 return render_template('students.html', students=students, programs=[], page_title="All Cases (Admin View)")
            
            # Auto-heal: If logged-in user is a Counsellor but missing from Counsellor table, add them
            if session.get('role') in ['Counsellor', 'Counselor']:
                try:
                    conn.execute("INSERT INTO Counsellor (name, contact) VALUES (?, '')", (user_full_name,))
                    conn.commit()
                    # Fetch again
                    counsellor = conn.execute("SELECT id FROM Counsellor WHERE name = ?", (user_full_name,)).fetchone()
                except Exception as e:
                    print(f"[MY_CASES] Auto-create failed: {e}")
            
            if not counsellor:
                flash(f"Error: Professional profile not found for '{user_full_name}'. Please contact Admin.", "error")
                conn.close()
                return redirect(url_for('dashboard'))
            
        counsellor_id = counsellor['id']
        
        # 2. Find students who have appointments with this counsellor (Past or Future)
        # We use DISTINCT to avoid duplicates
        students = conn.execute('''
            SELECT DISTINCT s.* 
            FROM Student s
            JOIN Appointment a ON s.id = a.student_id
            WHERE a.Counsellor_id = ?
            ORDER BY a.date DESC
        ''', (counsellor_id,)).fetchall()
        
        conn.close()
        
        return render_template('students.html', students=students, programs=[], page_title="My Calls List")
        
    except Exception as e:
        print(f"[MY_CASES] Error: {e}")
        return redirect(url_for('dashboard'))
@app.route('/download_report_file/<int:report_id>')
@login_required
def download_report_file(report_id):
    """Download the actual report file (DOCX)"""
    conn = get_db_connection()
    
    report = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
    conn.close()
    
    if not report:
        flash('Report not found', 'error')
        return redirect(url_for('reports_list'))
    
    # Convert Row to dict for easier access
    report_dict = dict(report)
    file_path = report_dict.get('file_path')
    
    if not file_path:
        flash('Report file path not found', 'error')
        return redirect(url_for('reports_list'))
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
    else:
        flash('Report file not found on disk', 'error')
        return redirect(url_for('reports_list'))

@app.route('/students')
@login_required
def students():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        students_raw = []
        program_rows = []
        try:
            # Get all students and their information
            students_raw = conn.execute('''
                SELECT s.*, 
                       COUNT(DISTINCT sess.id) as session_count
                FROM Student s
                LEFT JOIN Appointment a ON s.id = a.student_id
                LEFT JOIN session sess ON a.id = sess.appointment_id
                GROUP BY s.id
                ORDER BY s.name
            ''').fetchall()

            # Get all unique programs for the filter dropdown (extract as strings, not Row objects)
            program_rows = conn.execute("SELECT DISTINCT programme FROM Student WHERE programme IS NOT NULL AND programme != '' ORDER BY programme").fetchall()
        except Exception as e:
            print(f"[STUDENTS] Error getting students: {e}")
            students_raw = []
            program_rows = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Convert to list and add professional IDs
        students = []
        for student in students_raw:
            student_dict = dict(student)
            student_db_id = student_dict.get('id', 0)
            student_dict['professional_id'] = f"C{student_db_id:03d}"
            students.append(student_dict)

        programs = [row['programme'] for row in program_rows] if program_rows else []  # Convert Row objects to strings
        
        return render_template('students.html', students=students, programs=programs)
    except Exception as e:
        print(f"[STUDENTS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading students. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/student_profile/<int:id>')
@login_required
def student_profile(id):
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        # Get student information
        student = None
        sessions = []
        referrals = []
        try:
            student = conn.execute('SELECT * FROM Student WHERE id = ?', (id,)).fetchone()
        except Exception as e:
            print(f"[STUDENT_PROFILE] Error getting student: {e}")

        if not student:
            try:
                conn.close()
            except Exception:
                pass
            flash('Student not found', 'error')
            return redirect(url_for('students'))

        # Get all sessions for this student
        try:
            sessions = conn.execute('''
                SELECT sess.id, sess.session_type, sess.notes, sess.created_at,
                       s.name as student_name,
                       c.name as Counsellor_name,
                       a.date, a.time, a.status
                FROM session sess
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                WHERE s.id = ?
                ORDER BY sess.created_at DESC
            ''', (id,)).fetchall()
        except Exception as e:
            print(f"[STUDENT_PROFILE] Error getting sessions: {e}")
            sessions = []

        # Get all referrals for this student
        try:
            referrals = conn.execute('''
                SELECT r.id, r.referred_by, r.contact, r.reasons, r.action_taken, r.outcome, r.created_at
                FROM Referral r
                JOIN Session sess ON r.session_id = sess.id
                JOIN Appointment a ON sess.appointment_id = a.id
                WHERE a.student_id = ?
                ORDER BY r.created_at DESC
            ''', (id,)).fetchall()
        except Exception as e:
            print(f"[STUDENT_PROFILE] Error getting referrals: {e}")
            referrals = []

        # Get DASS-21 scores if table exists
        dass21_scores = []
        try:
            dass21_scores = conn.execute('''
                SELECT depression_score, anxiety_score, stress_score, completion_date, created_at
                FROM DASS21
                WHERE student_id = ?
                ORDER BY created_at DESC
            ''', (id,)).fetchall()
        except Exception as e:
            print(f"[STUDENT_PROFILE] Error getting DASS21 scores: {e}")
            dass21_scores = []

        # Get OQ-45.2 scores if table exists
        oq_scores = []
        try:
            oq_scores = conn.execute('''
                SELECT total_score, completion_date, created_at,
                       (SELECT created_at FROM session WHERE id = OutcomeQuestionnaire.session_id) as session_date
                FROM OutcomeQuestionnaire
                WHERE student_id = ?
                ORDER BY created_at DESC
            ''', (id,)).fetchall()
        except Exception as e:
            print(f"[STUDENT_PROFILE] Error getting OQ scores: {e}")
            oq_scores = []

        try:
            conn.close()
        except Exception:
            pass

        return render_template('student_profile.html', 
                             student=student, 
                             sessions=sessions,
                             referrals=referrals,
                             dass21_scores=dass21_scores,
                             oq_scores=oq_scores)
    except Exception as e:
        print(f"[STUDENT_PROFILE] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading student profile. Please try again.', 'error')
        return redirect(url_for('students'))

@app.route('/export_students')
@login_required
def export_students():
    import csv
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    
    # Get format parameter (default to csv for backward compatibility)
    export_format = request.args.get('format', 'csv').lower()
    
    conn = get_db_connection()
    
    # Get all students data with professional ID
    students_raw = conn.execute('''
        SELECT s.*, 
               COUNT(DISTINCT sess.id) as session_count
        FROM Student s
        LEFT JOIN Appointment a ON s.id = a.student_id
        LEFT JOIN Session sess ON a.id = sess.appointment_id
        GROUP BY s.id
        ORDER BY s.name
    ''').fetchall()
    
    conn.close()
    
    # Generate professional IDs
    students = []
    for student in students_raw:
        student_dict = dict(student)
        student_db_id = student_dict.get('id', 0)
        student_dict['professional_id'] = f"C{student_db_id:03d}"
        students.append(student_dict)
    
    if export_format == 'excel':
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Students"
        
        # Define header style
        header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        header_font = Font(bold=True)
        
        # Write headers
        headers = ['ID', 'Professional ID', 'Name', 'Index Number', 'Age', 'Gender', 'Email', 'Phone', 'Program', 'Department', 'Session Count', 'Created Date']
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Write data rows
        for row_num, student in enumerate(students, 2):
            ws.cell(row=row_num, column=1, value=student['id'])
            ws.cell(row=row_num, column=2, value=student['professional_id'])
            ws.cell(row=row_num, column=3, value=student['name'])
            ws.cell(row=row_num, column=4, value=student['index_number'] or 'N/A')
            ws.cell(row=row_num, column=5, value=student.get('age') or 'N/A')
            ws.cell(row=row_num, column=6, value=student.get('gender') or 'N/A')
            ws.cell(row=row_num, column=7, value=student.get('email') or 'N/A')
            ws.cell(row=row_num, column=8, value=student['contact'] or 'N/A')
            ws.cell(row=row_num, column=9, value=student.get('programme') or student.get('program') or 'N/A')
            ws.cell(row=row_num, column=10, value=student.get('department') or 'N/A')
            ws.cell(row=row_num, column=11, value=student['session_count'])
            ws.cell(row=row_num, column=12, value=student['created_at'])
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[col_letter].width = adjusted_width
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=students_export.xlsx'
        return response
    else:
        # Create CSV (default)
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Professional ID', 'Name', 'Index Number', 'Email', 'Phone', 'Program', 'Session Count', 'Created Date'])

        # Write data rows
        for student in students:
            writer.writerow([
                student['id'],
                student['professional_id'],
                student['name'],
                student['index_number'] or 'N/A',
                student.get('email') or 'N/A',
                student['contact'] or 'N/A',
                student.get('programme') or student.get('program') or 'N/A',
                student['session_count'],
                student['created_at']
            ])

        # Prepare response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=students_export.csv'

        return response

@app.route('/export_sessions')
@login_required
def export_sessions():
    import csv
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    
    # Get format parameter (default to csv for backward compatibility)
    export_format = request.args.get('format', 'csv').lower()
    
    conn = get_db_connection()
    
    # Get all sessions with full details
    sessions = conn.execute('''
        SELECT sess.id, sess.session_type, sess.notes, sess.created_at,
               s.name as student_name, s.id as student_db_id,
               c.name as Counsellor_name,
               a.date, a.time, a.status as appointment_status
        FROM session sess
        LEFT JOIN Appointment a ON sess.appointment_id = a.id
        LEFT JOIN Student s ON a.student_id = s.id
        LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
        ORDER BY sess.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    if export_format == 'excel':
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Sessions"
        
        # Define header style
        header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        header_font = Font(bold=True)
        
        # Write headers
        headers = ['ID', 'Date', 'Time', 'Student Name', 'Student ID', 'Counsellor', 'Session Type', 'Status', 'Notes', 'Created At']
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Write data rows
        for row_num, session in enumerate(sessions, 2):
            student_db_id = session.get('student_db_id', 0) if session.get('student_db_id') else 0
            professional_id = f"C{student_db_id:03d}" if student_db_id else 'N/A'
            
            ws.cell(row=row_num, column=1, value=session['id'])
            ws.cell(row=row_num, column=2, value=session['date'] or 'N/A')
            ws.cell(row=row_num, column=3, value=session['time'] or 'N/A')
            ws.cell(row=row_num, column=4, value=session['student_name'] or 'N/A')
            ws.cell(row=row_num, column=5, value=professional_id)
            ws.cell(row=row_num, column=6, value=session['Counsellor_name'] or 'N/A')
            ws.cell(row=row_num, column=7, value=session['session_type'] or 'N/A')
            ws.cell(row=row_num, column=8, value=session['appointment_status'] or 'N/A')
            ws.cell(row=row_num, column=9, value=session['notes'] or 'N/A')
            ws.cell(row=row_num, column=10, value=session['created_at'])
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[col_letter].width = adjusted_width
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=sessions_export.xlsx'
        return response
    else:
        # Create CSV (default)
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Date', 'Time', 'Student Name', 'Student ID', 'Counsellor', 'Session Type', 'Status', 'Notes', 'Created At'])

        # Write data rows
        for session in sessions:
            student_db_id = session.get('student_db_id', 0) if session.get('student_db_id') else 0
            professional_id = f"C{student_db_id:03d}" if student_db_id else 'N/A'

            writer.writerow([
                session['id'],
                session['date'] or 'N/A',
                session['time'] or 'N/A',
                session['student_name'] or 'N/A',
                professional_id,
                session['Counsellor_name'] or 'N/A',
                session['session_type'] or 'N/A',
                session['appointment_status'] or 'N/A',
                (session['notes'] or '').replace('\n', ' ')[:200],
                session['created_at']
            ])

        # Prepare response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=sessions_export.csv'
    
    return response

@app.route('/referral', methods=['GET', 'POST'])
@login_required
def referral():
    try:
        ensure_database_initialized()
        
        if request.method == 'POST':
            # Get form data
            session_id = request.form.get('session_id')
            referred_by = request.form.get('referred_by')
            contact = request.form.get('contact')
            action_taken = request.form.get('action_taken', '')
            outcome = request.form.get('outcome', '')

            # Get selected referral reasons (checkboxes)
            selected_reasons = request.form.getlist('referral_reasons')
            other_reason_text = request.form.get('other_reason_text', '').strip()

            # Combine reasons
            reasons_list = selected_reasons.copy()
            if 'Something Else' in selected_reasons and other_reason_text:
                # Replace "Something Else" with the actual text
                reasons_list.remove('Something Else')
                reasons_list.append(f'Something Else: {other_reason_text}')

            # Join reasons with commas, or use existing textarea value if checkboxes weren't used
            if reasons_list:
                reasons = ', '.join(reasons_list)
            else:
                reasons = request.form.get('reasons', '')  # Fallback to old textarea

            # Validate required fields
            if not all([session_id, referred_by, contact]) or not reasons:
                flash('Please fill in all required fields and select at least one reason', 'error')
                return redirect(url_for('referral'))

            # Insert referral into database
            conn = get_db_connection()
            if conn is None:
                flash('Database connection failed. Please restart the application.', 'error')
                return redirect(url_for('dashboard'))

            try:
                conn.execute('''
                    INSERT INTO Referral (session_id, referred_by, contact, reasons, action_taken, outcome, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, referred_by, contact, reasons, action_taken, outcome, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                flash('Referral created successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                conn.rollback()
                print(f"[REFERRAL] Error creating referral: {e}")
                flash(f'Error creating referral: {str(e)}', 'error')
                return redirect(url_for('referral'))
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
    
        # GET request - display referral form
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))

        sessions = []
        try:
            sessions = conn.execute('''
                SELECT s.id, s.created_at, st.name as student_name, st.index_number, c.name as Counsellor_name
                FROM session s
                JOIN Appointment a ON s.appointment_id = a.id
                JOIN Student st ON a.student_id = st.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                ORDER BY s.created_at DESC
            ''').fetchall()
        except Exception as e:
            print(f"[REFERRAL] Error getting sessions: {e}")
            sessions = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return render_template('referral.html', sessions=sessions)
    except Exception as e:
        print(f"[REFERRAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading referral page. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/all_referrals')
@login_required
def all_referrals():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        referrals = []
        try:
            # Get all referrals with student information
            referrals_raw = conn.execute('''
                SELECT r.id, r.session_id, r.referred_by, r.contact, r.reasons, r.created_at,
                               st.id as student_db_id, st.name as student_name, st.contact as student_contact, st.index_number
                FROM Referral r
                JOIN session sess ON r.session_id = sess.id
                JOIN Appointment a ON sess.appointment_id = a.id
                JOIN Student st ON a.student_id = st.id
                ORDER BY r.created_at DESC
            ''').fetchall()
            
            # Convert to list and add professional ID
            referrals = []
            for ref in referrals_raw:
                ref_dict = dict(ref)
                # Generate professional ID: C001, C002, etc. based on student database ID
                student_db_id = ref_dict.get('student_db_id', 0)
                professional_id = f"C{student_db_id:03d}"  # C001, C002, etc.
                ref_dict['professional_id'] = professional_id
                referrals.append(ref_dict)
        except Exception as e:
            print(f"[REFERRALS] Error getting referrals: {e}")
            referrals = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return render_template('referrals.html', referrals=referrals)
    except Exception as e:
        print(f"[REFERRALS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading referrals. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/export_referrals')
@login_required
def export_referrals():
    import csv
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    
    # Get format parameter (default to csv for backward compatibility)
    export_format = request.args.get('format', 'csv').lower()
    
    conn = get_db_connection()
    
    # Get all referrals with full details
    referrals_raw = conn.execute('''
        SELECT r.id, r.session_id, r.referred_by, r.contact, r.reasons, 
               r.action_taken, r.outcome, r.created_at,
               st.id as student_db_id, st.name as student_name, st.contact as student_contact
        FROM Referral r
        JOIN session sess ON r.session_id = sess.id
        JOIN Appointment a ON sess.appointment_id = a.id
        JOIN Student st ON a.student_id = st.id
        ORDER BY r.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    if export_format == 'excel':
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Referrals"
        
        # Define header style
        header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        header_font = Font(bold=True)
        
        # Write headers
        headers = ['ID', 'Date', 'Student Name', 'Student ID', 'Referred By', 'Contact', 'Reasons', 'Action Taken', 'Outcome']
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Write data rows with professional IDs
        for row_num, referral in enumerate(referrals_raw, 2):
            ref_dict = dict(referral)
            student_db_id = ref_dict.get('student_db_id', 0)
            professional_id = f"C{student_db_id:03d}"
            
            ws.cell(row=row_num, column=1, value=referral['id'])
            ws.cell(row=row_num, column=2, value=referral['created_at'])
            ws.cell(row=row_num, column=3, value=referral['student_name'] or 'N/A')
            ws.cell(row=row_num, column=4, value=professional_id)
            ws.cell(row=row_num, column=5, value=referral['referred_by'] or 'N/A')
            ws.cell(row=row_num, column=6, value=referral['contact'] or 'N/A')
            ws.cell(row=row_num, column=7, value=referral['reasons'] or 'N/A')
            ws.cell(row=row_num, column=8, value=referral['action_taken'] or 'N/A')
            ws.cell(row=row_num, column=9, value=referral['outcome'] or 'N/A')
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[col_letter].width = adjusted_width
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=referrals_export.xlsx'
        return response
    else:
        # Create CSV (default)
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header - using "Student ID" instead of "Student Contact"
        writer.writerow(['ID', 'Date', 'Student Name', 'Student ID', 'Referred By', 'Contact', 'Reasons', 'Action Taken', 'Outcome'])

        # Write data rows with professional IDs
        for referral in referrals_raw:
            ref_dict = dict(referral)
            # Generate professional ID: C001, C002, etc.
            student_db_id = ref_dict.get('student_db_id', 0)
            professional_id = f"C{student_db_id:03d}"

            writer.writerow([
                referral['id'],
                referral['created_at'],
                referral['student_name'] or 'N/A',
                professional_id,  # Use professional ID instead of phone number
                referral['referred_by'] or 'N/A',
                referral['contact'] or 'N/A',
                (referral['reasons'] or '').replace('\n', ' ')[:200],  # Limit length and replace newlines
                (referral['action_taken'] or '').replace('\n', ' ')[:200],
                (referral['outcome'] or '').replace('\n', ' ')[:200]
            ])

        # Prepare response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=referrals_export.csv'

        return response

@app.route('/outcome_questionnaire', methods=['GET', 'POST'])
@login_required
def outcome_questionnaire():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Get form data
            student_id = request.form.get('student_id')
            session_id = request.form.get('session_id')
            age = request.form.get('age')
            sex = request.form.get('sex')

            # Get all 25 item scores
            item_scores = []
            try:
                for i in range(1, 26):
                    score = request.form.get(f'item{i}')
                    if not score or score == '':
                        flash('Please fill in all item scores', 'error')
                        return redirect(url_for('outcome_questionnaire'))
                    item_scores.append(int(score))
            except ValueError:
                flash('Invalid score values. Please enter numbers only.', 'error')
                return redirect(url_for('outcome_questionnaire'))

            # Calculate total score
            total_score = sum(item_scores)

            # Insert questionnaire data into database
            try:
                # Use correct table name and column names (item1, item2, etc. without underscores)
                conn.execute('''
                    INSERT INTO OutcomeQuestionnaire 
                    (student_id, session_id, age, sex, item1, item2, item3, item4, item5,
                     item6, item7, item8, item9, item10, item11, item12, item13, item14, item15,
                     item16, item17, item18, item19, item20, item21, item22, item23, item24, item25,
                     total_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, session_id, age if age else None, sex if sex else None, *item_scores, total_score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                flash('Outcome questionnaire submitted successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                conn.rollback()
                print(f"[OUTCOME_QUESTIONNAIRE] Error saving: {e}")
                flash(f'Error submitting questionnaire: {str(e)}', 'error')
                return redirect(url_for('outcome_questionnaire'))
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        # GET request - display the form
        students_raw = []
        sessions_raw = []
        try:
            students_raw = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
            sessions_raw = conn.execute('''
                SELECT sess.id, sess.created_at, a.student_id, s.id as student_db_id, s.name as student_name
                FROM session sess
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                WHERE a.student_id IS NOT NULL
                ORDER BY sess.created_at DESC
            ''').fetchall()
        except Exception as e:
            print(f"[OUTCOME_QUESTIONNAIRE] Error getting dropdown data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        # Convert students to list
        students = []
        for student in students_raw:
            students.append(dict(student))
        
        # Convert sessions to list and format dates
        sessions = []
        for sess in sessions_raw:
            sess_dict = dict(sess)
            # Format created_at for display
            if sess_dict.get('created_at'):
                try:
                    dt = datetime.strptime(sess_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                    sess_dict['created_at_formatted'] = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    sess_dict['created_at_formatted'] = sess_dict['created_at']
            else:
                sess_dict['created_at_formatted'] = 'N/A'
            
            # Add professional ID
            student_db_id = sess_dict.get('student_db_id', 0)
            sess_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
            sessions.append(sess_dict)
        
        return render_template('outcome_questionnaire.html', students=students, sessions=sessions)
    except Exception as e:
        print(f"[OUTCOME_QUESTIONNAIRE] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading outcome questionnaire page. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/dass21', methods=['GET', 'POST'])
@login_required
def dass21():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Get form data
            student_id = request.form.get('student_id', '').strip()
            depression_score = request.form.get('depression_score', '0')
            anxiety_score = request.form.get('anxiety_score', '0')
            stress_score = request.form.get('stress_score', '0')
            
            # Validate required fields
            if not student_id or student_id == '':
                flash('Please select a student', 'error')
                try:
                    students_raw = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
                    students = [dict(s) for s in students_raw]
                except Exception as e:
                    print(f"[DASS21] Error getting students: {e}")
                    students = []
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
                return render_template('dass21.html', students=students)
            
            try:
                depression_score = float(depression_score)
                anxiety_score = float(anxiety_score)
                stress_score = float(stress_score)
            except ValueError:
                flash('Please enter valid numeric scores', 'error')
                try:
                    students_raw = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
                    students = [dict(s) for s in students_raw]
                except Exception as e:
                    print(f"[DASS21] Error getting students: {e}")
                    students = []
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
                return render_template('dass21.html', students=students)
            
            # Calculate final scores (multiply by 2)
            final_depression = depression_score * 2
            final_anxiety = anxiety_score * 2
            final_stress = stress_score * 2
            
            # Insert DASS-21 scores into database
            try:
                conn.execute('''
                    INSERT INTO DASS21 
                    (student_id, depression_score, anxiety_score, stress_score, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, depression_score, anxiety_score, stress_score,
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                flash('DASS-21 scores saved successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                conn.rollback()
                print(f"[DASS21] Error saving scores: {e}")
                import traceback
                traceback.print_exc()
                flash(f'Error saving DASS-21 scores: {str(e)}', 'error')
                try:
                    students_raw = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
                    students = [dict(s) for s in students_raw]
                except Exception as e:
                    print(f"[DASS21] Error getting students: {e}")
                    students = []
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
                return render_template('dass21.html', students=students)
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        
        # GET request - display the form
        students_raw = []
        try:
            students_raw = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
        except Exception as e:
            print(f"[DASS21] Error getting students: {e}")
            students_raw = []
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        # Convert to list
        students = []
        for student in students_raw:
            students.append(dict(student))
        
        return render_template('dass21.html', students=students)
    except Exception as e:
        print(f"[DASS21] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading DASS-21 page. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        if 'confirm' in request.form:
            # Process confirmed import
            import_type = request.form.get('import_type')
            confirmed_data = request.form.get('confirmed_data')
            
            if not confirmed_data:
                flash('No data to import', 'error')
                return redirect(url_for('import_csv'))
            
            try:
                data = json.loads(confirmed_data)
                conn = get_db_connection()
                
                if import_type == 'students':
                    # Import students data
                    for row in data:
                        conn.execute('''
                            INSERT OR REPLACE INTO students 
                            (student_id, first_name, last_name, email, phone, department, programme, parent_contact)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            row.get('index_number', ''),
                            row.get('name', '').split()[0] if ' ' in row.get('name', '') else row.get('name', ''),
                            row.get('name', '').split()[-1] if ' ' in row.get('name', '') else '',
                            row.get('email', ''),
                            row.get('phone', ''),
                            row.get('department', ''),
                            row.get('programme', ''),
                            row.get('parent_contact', '')
                        ))
                
                elif import_type == 'appointments':
                    # Import appointments data
                    for row in data:
                        # Get student_id from student_name
                        student_name = row.get('student_name', '')
                        student = conn.execute(
                            'SELECT id FROM Student WHERE name = ? OR id = ?',
                            (student_name, student_name)
                        ).fetchone()
                        
                        if student:
                            conn.execute('''
                                INSERT INTO Appointment 
                                (student_id, date, time, purpose, counselor_id, status)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                student['id'],
                                row.get('date', ''),
                                row.get('time', ''),
                                row.get('purpose', ''),
                                session.get('user_id'),
                                row.get('status', 'scheduled')
                            ))
                
                conn.commit()
                conn.close()
                
                flash(f'Successfully imported {len(data)} {import_type}', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error importing data: {str(e)}', 'error')
                return redirect(url_for('import_csv'))
        
        else:
            # Handle file upload and preview
            import_type = request.form.get('import_type')
            csv_file = request.files.get('csv_file')
            
            if not import_type or not csv_file:
                flash('Please select import type and CSV file', 'error')
                return redirect(url_for('import_csv'))
            
            try:
                # Read CSV file
                csv_data = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(csv_data)
                
                preview_data = []
                errors = []
                
                # Validate and prepare data
                for row_num, row in enumerate(csv_reader, start=2):
                    if import_type == 'students':
                        # Validate student data
                        if not row.get('name') or not row.get('index_number'):
                            errors.append(f'Row {row_num}: Missing required fields (name, index_number)')
                        else:
                            preview_data.append({
                                'name': row.get('name', ''),
                                'index_number': row.get('index_number', ''),
                                'email': row.get('email', ''),
                                'phone': row.get('phone', ''),
                                'department': row.get('department', ''),
                                'programme': row.get('programme', ''),
                                'parent_contact': row.get('parent_contact', '')
                            })
                    
                    elif import_type == 'appointments':
                        # Validate appointment data
                        if not row.get('student_name') or not row.get('date') or not row.get('time'):
                            errors.append(f'Row {row_num}: Missing required fields (student_name, date, time)')
                        else:
                            preview_data.append({
                                'student_name': row.get('student_name', ''),
                                'date': row.get('date', ''),
                                'time': row.get('time', ''),
                                'counsellor': row.get('counsellor', ''),
                                'purpose': row.get('purpose', ''),
                                'status': row.get('status', 'scheduled')
                            })
                
                if not preview_data:
                    flash('No valid data found in CSV file', 'error')
                    return redirect(url_for('import_csv'))
                
                return render_template('import_csv.html', 
                                     preview_data=preview_data,
                                     headers=list(preview_data[0].keys()) if preview_data else [],
                                     errors=errors,
                                     import_type=import_type,
                                     confirmed_data=json.dumps(preview_data))
                
            except Exception as e:
                flash(f'Error reading CSV file: {str(e)}', 'error')
                return redirect(url_for('import_csv'))
    
    # GET request - display the form
    return render_template('import_csv.html')

@app.route('/intake', methods=['GET', 'POST'])
@login_required
def intake():
    """
    Phase 1: Secretary Intake Flow
    - Registers new student (if needed)
    - Creates Appointment
    - Records Urgency, Purpose, and Referral Source
    - Sets status to 'Scheduled' (Pending Handover)
    """
    if request.method == 'POST':
        conn = get_db_connection()
        try:
            # 1. Extract Student Info
            name = request.form.get('name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            index_number = request.form.get('index_number')
            department = request.form.get('department')
            faculty = request.form.get('faculty')
            programme = request.form.get('programme')
            contact = request.form.get('contact')
            parent_contact = request.form.get('parent_contact')
            hall = request.form.get('hall_of_residence')
            
            # 2. Extract Appointment/Intake Info
            appt_date = request.form.get('appointment_date')
            appt_time = request.form.get('appointment_time')
            purpose = request.form.get('purpose')
            urgency = request.form.get('urgency')
            referral = request.form.get('referral_source')
            
            # 3. Create/Check Student
            # Determine logic: assume New Client per form design, but check index_number to avoid dupes
            existing_student = conn.execute("SELECT id FROM Student WHERE index_number = ?", (index_number,)).fetchone()
            
            if existing_student:
                student_id = existing_student['id']
                # Optional: Update contact info if changed
            else:
                cursor = conn.execute('''
                    INSERT INTO Student (name, age, gender, index_number, department, 
                    faculty, programme, contact, parent_contact, hall_of_residence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, age, gender, index_number, department, faculty, programme, contact, parent_contact, hall))
                student_id = cursor.lastrowid
                
            # 4. Create Appointment (The "Intake Record")
            conn.execute('''
                INSERT INTO Appointment (student_id, date, time, purpose, status, urgency, referral_source)
                VALUES (?, ?, ?, ?, 'Scheduled', ?, ?)
            ''', (student_id, appt_date, appt_time, purpose, urgency, referral))
            
            conn.commit()
            flash('Student intake registered and appointment scheduled successfully.', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error processing intake: {str(e)}', 'danger')
            return redirect(url_for('intake'))
        finally:
            conn.close()

    return render_template('intake.html', now=datetime.now())

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Get form data
            student_id = request.form.get('student_id')
            appointment_date = request.form.get('date')
            appointment_time = request.form.get('time')
            purpose = request.form.get('purpose')
            counselor_id = request.form.get('counselor_id')
            urgency = request.form.get('urgency', 'Normal')
            referral = request.form.get('referral_source', 'Self')

            students = []
            counsellors = []
            try:
                students = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
                counsellors = conn.execute('SELECT id, name FROM Counsellor ORDER BY name').fetchall()
            except Exception as e:
                print(f"[APPOINTMENT] Error getting dropdown data: {e}")

            # Validate data
            if not student_id or not appointment_date or not appointment_time or not counselor_id:
                try:
                    conn.close()
                except Exception:
                    pass
                flash('Please fill in all required fields', 'danger')
                return render_template('appointment.html', students=students, Counsellors=counsellors)

            # Check if student exists
            try:
                student = conn.execute('SELECT * FROM Student WHERE id = ?', (student_id,)).fetchone()
            except Exception as e:
                print(f"[APPOINTMENT] Error checking student: {e}")
                student = None

            if not student:
                try:
                    conn.close()
                except Exception:
                    pass
                flash('Student not found. Please check the ID or add the student first.', 'danger')
                return render_template('appointment.html', students=students, Counsellors=counsellors)

            # Save appointment to database
            try:
                conn.execute('''
                        INSERT INTO Appointment (student_id, date, time, purpose, Counsellor_id, status, urgency, referral_source)
                    VALUES (?, ?, ?, ?, ?, 'Scheduled', ?, ?)
                ''', (student_id, appointment_date, appointment_time, purpose, counselor_id, urgency, referral))
                conn.commit()
                flash('Appointment scheduled successfully!', 'success')
                return redirect(url_for('manage_appointments'))
            except Exception as e:
                conn.rollback()
                print(f"[APPOINTMENT] Error saving appointment: {e}")
                flash(f'Error scheduling appointment: {str(e)}', 'danger')
                return render_template('appointment.html', students=students, Counsellors=counsellors)
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
        
        # GET request - display the form
        students = []
        counsellors = []
        try:
            students = conn.execute('SELECT id, name, programme FROM Student ORDER BY name').fetchall()
            counsellors = conn.execute('SELECT id, name FROM Counsellor ORDER BY name').fetchall()
        except Exception as e:
            print(f"[APPOINTMENT] Error getting dropdown data: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
        return render_template('appointment.html', 
                             students=students, 
                             Counsellors=counsellors, 
                             selected_student_id=request.args.get('student_id'))
    except Exception as e:
        print(f"[APPOINTMENT] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading appointment page. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/manage_appointments')
@login_required
def manage_appointments():
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
    
        appointments = []
        try:
            # Get all appointments with student and counsellor names
            appointments = conn.execute('''
                SELECT a.*, s.name as student_name, c.name as Counsellor_name
                FROM Appointment a
                LEFT JOIN Student s ON a.student_id = s.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                ORDER BY a.date DESC, a.time DESC
            ''').fetchall()
        except Exception as e:
            print(f"[APPOINTMENTS] Error getting appointments: {e}")
            appointments = []
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        return render_template('appointments.html', appointments=appointments)
    except Exception as e:
        print(f"[APPOINTMENTS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading appointments. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/update_appointment_status/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    """Update the status of an appointment"""
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required', 'error')
        return redirect(url_for('manage_appointments'))
    
    # Valid statuses
    valid_statuses = ['Scheduled', 'Sent to Counsellor', 'In Session', 'Completed', 'Cancelled', 'Postponed']
    if new_status not in valid_statuses:
        flash('Invalid status', 'error')
        return redirect(url_for('manage_appointments'))
    
    conn = get_db_connection()
    try:
        # Check if appointment exists
        appointment = conn.execute('SELECT id FROM Appointment WHERE id = ?', (appointment_id,)).fetchone()
        
        if not appointment:
            flash('Appointment not found', 'error')
            return redirect(url_for('manage_appointments'))
        
        # Update the status
        conn.execute('''
            UPDATE Appointment 
            SET status = ? 
            WHERE id = ?
        ''', (new_status, appointment_id))
        conn.commit()
        
        flash(f'Appointment status updated to {new_status} successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error updating appointment status: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage_appointments'))

# ---------- Print Routes ----------
@app.route('/view_report/<int:report_id>')
@login_required
def view_report(report_id):
    conn = get_db_connection()
    
    # Get report details
    report = conn.execute('''
        SELECT * FROM reports WHERE id = ?
    ''', (report_id,)).fetchone()
    
    if not report:
        conn.close()
        flash('Report not found', 'error')
        return redirect(url_for('reports_list'))
    
    conn.close()
    # Convert Row to dict for easier template access
    report_dict = dict(report)
    return render_template('view_report.html', report=report_dict, now=datetime.utcnow())

@app.route('/download_report/<int:report_id>')
@login_required
def download_report(report_id):
    conn = get_db_connection()
    
    # Get report details
    report = conn.execute('''
        SELECT * FROM reports WHERE id = ?
    ''', (report_id,)).fetchone()
    
    if not report:
        conn.close()
        flash('Report not found', 'error')
        return redirect(url_for('reports_list'))
    
    conn.close()
    
    # For now, redirect to print report as download functionality
    # This can be enhanced to generate actual downloadable files
    return redirect(url_for('print_report', report_id=report_id))

@app.route('/delete_report/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    conn = get_db_connection()
    
    # Delete report from database
    try:
        result = conn.execute('DELETE FROM reports WHERE id = ?', (report_id,)).rowcount
        conn.commit()
        
        if result > 0:
            flash('Report deleted successfully!', 'success')
        else:
            flash('Report not found', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting report: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('reports_list'))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete a student and all related records"""
    conn = get_db_connection()
    
    try:
        # Check if student exists
        student = conn.execute('SELECT * FROM Student WHERE id = ?', (student_id,)).fetchone()
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('students'))
        
        # Delete related records first (due to foreign keys)
        # Delete referrals (through sessions through appointments)
        conn.execute('''
            DELETE FROM Referral 
            WHERE session_id IN (
                SELECT s.id FROM session s
                JOIN Appointment a ON s.appointment_id = a.id
                WHERE a.student_id = ?
            )
        ''', (student_id,))
        
        # Delete sessions
        conn.execute('''
            DELETE FROM session
            WHERE appointment_id IN (
                SELECT id FROM Appointment WHERE student_id = ?
            )
        ''', (student_id,))
        
        # Delete appointments
        conn.execute('DELETE FROM Appointment WHERE student_id = ?', (student_id,))
        
        # Delete assessments
        conn.execute('DELETE FROM DASS21 WHERE student_id = ?', (student_id,))
        conn.execute('DELETE FROM OutcomeQuestionnaire WHERE student_id = ?', (student_id,))
        
        # Finally delete the student
        result = conn.execute('DELETE FROM Student WHERE id = ?', (student_id,)).rowcount
        conn.commit()
        
        if result > 0:
            flash('Student and all related records deleted successfully!', 'success')
        else:
            flash('Student not found', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting student: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('students'))

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    """Delete an appointment and related sessions"""
    conn = get_db_connection()
    
    try:
        # Check if appointment exists
        appointment = conn.execute('SELECT * FROM Appointment WHERE id = ?', (appointment_id,)).fetchone()
        if not appointment:
            flash('Appointment not found', 'error')
            return redirect(url_for('manage_appointments'))
        
        # Delete related sessions first
        conn.execute('DELETE FROM session WHERE appointment_id = ?', (appointment_id,))
        
        # Delete the appointment
        result = conn.execute('DELETE FROM Appointment WHERE id = ?', (appointment_id,)).rowcount
        conn.commit()
        
        if result > 0:
            flash('Appointment deleted successfully!', 'success')
        else:
            flash('Appointment not found', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting appointment: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manage_appointments'))

@app.route('/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    """Delete a session and related records"""
    conn = get_db_connection()
    
    try:
        # Check if session exists
        session_record = conn.execute('SELECT * FROM session WHERE id = ?', (session_id,)).fetchone()
        if not session_record:
            flash('Session not found', 'error')
            return redirect(url_for('sessions_list'))
        
        # Delete related referrals
        conn.execute('DELETE FROM Referral WHERE session_id = ?', (session_id,))
        
        # Delete case management records
        conn.execute('DELETE FROM CaseManagement WHERE session_id = ?', (session_id,))
        
        # Delete the session
        result = conn.execute('DELETE FROM session WHERE id = ?', (session_id,)).rowcount
        conn.commit()
        
        if result > 0:
            flash('Session deleted successfully!', 'success')
        else:
            flash('Session not found', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting session: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('sessions_list'))

@app.route('/delete_referral/<int:referral_id>', methods=['POST'])
@login_required
def delete_referral(referral_id):
    """Delete a referral"""
    conn = get_db_connection()
    
    try:
        result = conn.execute('DELETE FROM Referral WHERE id = ?', (referral_id,)).rowcount
        conn.commit()
        
        if result > 0:
            flash('Referral deleted successfully!', 'success')
        else:
            flash('Referral not found', 'error')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting referral: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('all_referrals'))

@app.route('/get_session/<int:session_id>')
@login_required
def get_session(session_id):
    """Get session details as JSON for the modal"""
    conn = get_db_connection()
    
    try:
        session_data = conn.execute('''
            SELECT sess.id, sess.session_type, sess.notes, sess.outcome, sess.created_at,
                   s.name as student_name,
                   c.name as Counsellor_name,
                   a.date, a.time, a.status as appointment_status
            FROM session sess
            LEFT JOIN Appointment a ON sess.appointment_id = a.id
            LEFT JOIN Student s ON a.student_id = s.id
            LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
            WHERE sess.id = ?
        ''', (session_id,)).fetchone()
        
        if not session_data:
            conn.close()
            return jsonify({'error': 'Session not found'}), 404
        
        # Convert to dict for JSON serialization
        session_dict = {
            'id': session_data['id'],
            'student_name': session_data['student_name'] or 'N/A',
            'Counsellor_name': session_data['Counsellor_name'] or 'N/A',
            'date': session_data['date'] or 'N/A',
            'time': session_data['time'] or 'N/A',
            'session_type': session_data['session_type'] or 'N/A',
            'appointment_status': session_data['appointment_status'] or 'N/A',
            'notes': session_data['notes'] or 'No notes provided',
            'outcome': session_data['outcome'] or 'N/A',
            'created_at': session_data['created_at']
        }
        
        conn.close()
        return jsonify(session_dict)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/print_session/<int:session_id>')
@login_required
def print_session(session_id):
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
    
    # Get session details with student information
        session_data = None
        try:
            session_data = conn.execute('''
                SELECT sess.*, s.name as student_name, 
                       s.index_number, s.programme, s.contact, s.department,
                       c.name as Counsellor_name,
                       a.date, a.time, a.status as appointment_status
                FROM session sess
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                LEFT JOIN Counsellor c ON a.Counsellor_id = c.id
                WHERE sess.id = ?
            ''', (session_id,)).fetchone()
        except Exception as e:
            print(f"[PRINT_SESSION] Error getting session: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
        if not session_data:
            flash('Session not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('print_session.html', session_data=session_data)
    except Exception as e:
        print(f"[PRINT_SESSION] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading session for printing.', 'error')
        return redirect(url_for('sessions_list'))

@app.route('/print_referral/<int:id>')
@login_required
def print_referral(id):
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
    
    # Get referral details with student information
        referral = None
        student_info = None
        try:
            referral = conn.execute('''
                SELECT r.*, s.id as student_db_id, s.name as student_name, 
                       s.index_number, s.contact as student_contact, s.department as student_department,
                       sess.created_at as session_date,
                       a.date as appointment_date, a.time as appointment_time
                FROM Referral r
                JOIN session sess ON r.session_id = sess.id
                JOIN Appointment a ON sess.appointment_id = a.id
                JOIN Student s ON a.student_id = s.id
        WHERE r.id = ?
    ''', (id,)).fetchone()
    
            # Parse reasons from comma-separated string
            reasons_str = referral['reasons'] or ''
            referral_reasons_list = [r.strip() for r in reasons_str.split(',') if r.strip()]
            
            # Check for "Something Else" and extract text
            other_reason_text = None
            if referral_reasons_list:
                for idx, reason in enumerate(referral_reasons_list):
                    if reason.startswith('Something Else:'):
                        other_reason_text = reason.replace('Something Else:', '').strip()
                        referral_reasons_list[idx] = 'Something Else'  # Replace with just the checkbox name
                        break
            
            # Convert to dict for template and add professional ID
            referral_dict = dict(referral) if referral else {}
            if referral and referral_dict.get('student_db_id'):
                student_db_id = referral_dict.get('student_db_id', 0)
                referral_dict['professional_id'] = f"C{student_db_id:03d}"
            else:
                referral_dict['professional_id'] = 'N/A'
            referral_dict['referral_reasons_list'] = referral_reasons_list
            referral_dict['other_reason_text'] = other_reason_text
            student_department = referral.get('student_department', 'N/A') if referral else 'N/A'
            
        except Exception as e:
            print(f"[PRINT_REFERRAL] Error getting referral: {e}")
            import traceback
            traceback.print_exc()
            referral = None
            referral_dict = None
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        if not referral or not referral_dict:
            # Only flash error if it's a legitimate "not found" case (not a database error)
            if referral is None:
                flash('Referral not found', 'error')
            else:
                flash('Error loading referral details. Please try again.', 'error')
            return redirect(url_for('all_referrals'))
    
        return render_template('print_referral.html', 
                             referral=referral_dict,
                             referral_reasons_list=referral_reasons_list,
                             other_reason_text=other_reason_text,
                             student_department=student_department)
    except Exception as e:
        print(f"[PRINT_REFERRAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading referral for printing.', 'error')
        return redirect(url_for('all_referrals'))

@app.route('/print_case/<int:case_id>')
@login_required
def print_case(case_id):
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
    
    # Get case details with student information
        case = None
        try:
            case = conn.execute('''
                SELECT cm.*, s.name as student_name, 
                       s.index_number, s.programme, s.contact,
                       sess.created_at as session_date
                FROM CaseManagement cm
                JOIN session sess ON cm.session_id = sess.id
                JOIN Appointment a ON sess.appointment_id = a.id
                JOIN Student s ON a.student_id = s.id
                WHERE cm.id = ?
            ''', (case_id,)).fetchone()
        except Exception as e:
            print(f"[PRINT_CASE] Error getting case: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
        if not case:
            flash('Case not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('print_case.html', case=case)
    except Exception as e:
        print(f"[PRINT_CASE] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading case for printing.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/case_notes_list')
@login_required
def case_notes_list():
    """Display all case notes linked to students"""
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        case_notes = []
        try:
            case_notes_raw = conn.execute('''
                SELECT cm.id, cm.session_id, cm.client_appearance, cm.problems, cm.interventions,
                       cm.recommendations, cm.next_visit_date, cm.counsellor_signature, cm.created_at,
                       s.id as student_db_id, s.name as student_name, s.index_number, s.programme,
                       sess.created_at as session_date
                FROM CaseManagement cm
                JOIN session sess ON cm.session_id = sess.id
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                ORDER BY cm.created_at DESC
            ''').fetchall()
            
            # Convert to list and add professional IDs
            for cn in case_notes_raw:
                cn_dict = dict(cn)
                student_db_id = cn_dict.get('student_db_id', 0)
                cn_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
                case_notes.append(cn_dict)
        except Exception as e:
            print(f"[CASE_NOTES_LIST] Error getting case notes: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        return render_template('case_notes_list.html', case_notes=case_notes)
    except Exception as e:
        print(f"[CASE_NOTES_LIST] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading case notes. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/dass21_list')
@login_required
def dass21_list():
    """Display all DASS-21 records linked to students"""
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        dass21_records = []
        try:
            dass21_raw = conn.execute('''
                SELECT d.id, d.student_id, d.depression_score, d.anxiety_score, d.stress_score,
                       d.created_at, d.completion_date,
                       s.id as student_db_id, s.name as student_name, s.index_number, s.programme
                FROM DASS21 d
                LEFT JOIN Student s ON d.student_id = s.id
                ORDER BY d.created_at DESC
            ''').fetchall()
            
            # Convert to list and add professional IDs and final scores
            for d in dass21_raw:
                d_dict = dict(d)
                student_db_id = d_dict.get('student_db_id', 0)
                d_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
                # Calculate final scores (x2)
                d_dict['final_depression'] = (d_dict.get('depression_score', 0) or 0) * 2
                d_dict['final_anxiety'] = (d_dict.get('anxiety_score', 0) or 0) * 2
                d_dict['final_stress'] = (d_dict.get('stress_score', 0) or 0) * 2
                dass21_records.append(d_dict)
        except Exception as e:
            print(f"[DASS21_LIST] Error getting DASS-21 records: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        return render_template('dass21_list.html', dass21_records=dass21_records)
    except Exception as e:
        print(f"[DASS21_LIST] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading DASS-21 records. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/print_case_note/<int:case_id>')
@login_required
def print_case_note(case_id):
    """Print case note"""
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        case = None
        try:
            case = conn.execute('''
                SELECT cm.*, s.id as student_db_id, s.name as student_name, 
                       s.index_number, s.programme, s.contact, s.department,
                       sess.created_at as session_date
                FROM CaseManagement cm
                JOIN session sess ON cm.session_id = sess.id
                LEFT JOIN Appointment a ON sess.appointment_id = a.id
                LEFT JOIN Student s ON a.student_id = s.id
                WHERE cm.id = ?
            ''', (case_id,)).fetchone()
            
            if case:
                case_dict = dict(case)
                student_db_id = case_dict.get('student_db_id', 0)
                case_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
                case = case_dict
        except Exception as e:
            print(f"[PRINT_CASE_NOTE] Error getting case: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        if not case:
            flash('Case note not found', 'error')
            return redirect(url_for('case_notes_list'))
        
        return render_template('print_case_note.html', case=case)
    except Exception as e:
        print(f"[PRINT_CASE_NOTE] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading case note for printing.', 'error')
        return redirect(url_for('case_notes_list'))

@app.route('/print_dass21/<int:dass21_id>')
@login_required
def print_dass21(dass21_id):
    """Print DASS-21 record"""
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        dass21_record = None
        try:
            dass21_raw = conn.execute('''
                SELECT d.*, s.id as student_db_id, s.name as student_name, 
                       s.index_number, s.programme, s.contact, s.department
                FROM DASS21 d
                LEFT JOIN Student s ON d.student_id = s.id
                WHERE d.id = ?
            ''', (dass21_id,)).fetchone()
            
            if dass21_raw:
                dass21_dict = dict(dass21_raw)
                student_db_id = dass21_dict.get('student_db_id', 0)
                dass21_dict['professional_id'] = f"C{student_db_id:03d}" if student_db_id else 'N/A'
                # Calculate final scores (x2)
                dass21_dict['final_depression'] = (dass21_dict.get('depression_score', 0) or 0) * 2
                dass21_dict['final_anxiety'] = (dass21_dict.get('anxiety_score', 0) or 0) * 2
                dass21_dict['final_stress'] = (dass21_dict.get('stress_score', 0) or 0) * 2
                dass21_record = dass21_dict
        except Exception as e:
            print(f"[PRINT_DASS21] Error getting DASS-21 record: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        
        if not dass21_record:
            flash('DASS-21 record not found', 'error')
            return redirect(url_for('dass21_list'))
        
        return render_template('print_dass21.html', dass21=dass21_record)
    except Exception as e:
        print(f"[PRINT_DASS21] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading DASS-21 record for printing.', 'error')
        return redirect(url_for('dass21_list'))

@app.route('/print_report/<int:report_id>')
@login_required
def print_report(report_id):
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
    
    # Get report details
        report = None
        try:
            report = conn.execute('''
                SELECT * FROM reports WHERE id = ?
            ''', (report_id,)).fetchone()
        except Exception as e:
            print(f"[PRINT_REPORT] Error getting report: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
        if not report:
            flash('Report not found', 'error')
            return redirect(url_for('reports_list'))
    
        # Convert Row to dict for easier template access
        report_dict = dict(report) if report else {}
        return render_template('print_report.html', report=report_dict, now=datetime.utcnow())
    except Exception as e:
        print(f"[PRINT_REPORT] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading report for printing.', 'error')
        return redirect(url_for('reports_list'))

@app.route('/statistics')
@login_required
def statistics():
    """Display comprehensive statistics with charts"""
    try:
        ensure_database_initialized()
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please restart the application.', 'error')
            return redirect(url_for('dashboard'))
        
        # Initialize with defaults
        total_students = 0
        total_appointments = 0
        total_sessions = 0
        total_referrals = 0
        gender_stats = []
        programme_stats = []
        level_stats = []
        appointment_status_stats = []
        
        try:
            # Overall Statistics
            result = conn.execute('SELECT COUNT(*) as count FROM Student').fetchone()
            total_students = result['count'] if result else 0
            
            result = conn.execute('SELECT COUNT(*) as count FROM Appointment').fetchone()
            total_appointments = result['count'] if result else 0
            
            result = conn.execute('SELECT COUNT(*) as count FROM session').fetchone()
            total_sessions = result['count'] if result else 0
            
            try:
                result = conn.execute('SELECT COUNT(*) as count FROM Referral').fetchone()
                total_referrals = result['count'] if result else 0
            except:
                total_referrals = 0
            
            # Students by Gender
            try:
                gender_stats = conn.execute('''
                    SELECT COALESCE(gender, 'Not Specified') as gender, COUNT(*) as count 
                    FROM Student 
                    GROUP BY gender
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting gender stats: {e}")
                gender_stats = []
            
            # Students by Programme
            try:
                programme_stats = conn.execute('''
                    SELECT COALESCE(programme, 'Not Specified') as programme, COUNT(*) as count 
                    FROM Student 
                    GROUP BY programme
                    ORDER BY count DESC
                    LIMIT 10
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting programme stats: {e}")
                programme_stats = []
            
            # Students by Department
            try:
                department_stats = conn.execute('''
                    SELECT COALESCE(department, 'Not Specified') as department, COUNT(*) as count 
                    FROM Student 
                    GROUP BY department
                    ORDER BY count DESC
                    LIMIT 10
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting department stats: {e}")
                department_stats = []
            
            # Appointments by Status
            try:
                appointment_status_stats = conn.execute('''
                    SELECT COALESCE(status, 'Not Specified') as status, COUNT(*) as count 
                    FROM Appointment 
                    GROUP BY status
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting appointment status stats: {e}")
                appointment_status_stats = []
            
            # Appointments Over Time (Last 6 Months)
            try:
                appointment_timeline = conn.execute('''
                    SELECT strftime('%Y-%m', date) as month, COUNT(*) as count 
                    FROM Appointment 
                    WHERE date >= date('now', '-6 months')
                    GROUP BY month
                    ORDER BY month
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting appointment timeline: {e}")
                appointment_timeline = []
            
            # Sessions Over Time (Last 6 Months)
            try:
                session_timeline = conn.execute('''
                    SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count 
                    FROM session 
                    WHERE created_at >= date('now', '-6 months')
                    GROUP BY month
                    ORDER BY month
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting session timeline: {e}")
                session_timeline = []
            
            # Sessions by Type
            try:
                session_type_stats = conn.execute('''
                    SELECT COALESCE(session_type, 'Not Specified') as session_type, COUNT(*) as count 
                    FROM session 
                    GROUP BY session_type
                    ORDER BY count DESC
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting session type stats: {e}")
                session_type_stats = []
            
            # Age Distribution
            try:
                age_distribution = conn.execute('''
                    SELECT 
                        CASE 
                            WHEN age < 18 THEN 'Under 18'
                            WHEN age BETWEEN 18 AND 20 THEN '18-20'
                            WHEN age BETWEEN 21 AND 25 THEN '21-25'
                            WHEN age BETWEEN 26 AND 30 THEN '26-30'
                            WHEN age > 30 THEN 'Over 30'
                            ELSE 'Not Specified'
                        END as age_group,
                        COUNT(*) as count
                    FROM Student
                    GROUP BY age_group
                    ORDER BY 
                        CASE age_group
                            WHEN 'Under 18' THEN 1
                            WHEN '18-20' THEN 2
                            WHEN '21-25' THEN 3
                            WHEN '26-30' THEN 4
                            WHEN 'Over 30' THEN 5
                            ELSE 6
                        END
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting age distribution: {e}")
                age_distribution = []
            
            # Top Counsellors by Appointments
            try:
                top_counsellors = conn.execute('''
                    SELECT c.name, COUNT(a.id) as appointment_count
                    FROM Counsellor c
                    LEFT JOIN Appointment a ON c.id = a.Counsellor_id
                    GROUP BY c.id, c.name
                    ORDER BY appointment_count DESC
                    LIMIT 5
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting top counsellors: {e}")
                top_counsellors = []
            
            # Monthly New Students (Last 6 Months)
            try:
                new_students_timeline = conn.execute('''
                    SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count 
                    FROM Student 
                    WHERE created_at >= date('now', '-6 months')
                    GROUP BY month
                    ORDER BY month
                ''').fetchall()
            except Exception as e:
                print(f"[STATISTICS] Error getting new students timeline: {e}")
                new_students_timeline = []
            
        except Exception as e:
            print(f"[STATISTICS] Error in statistics queries: {e}")
        finally:
            conn.close()
        
        # Convert to dictionaries for JSON serialization (use safe defaults if missing)
        stats_data = {
            'overall': {
                'total_students': total_students,
                'total_appointments': total_appointments,
                'total_sessions': total_sessions,
                'total_referrals': total_referrals
            },
            'gender': [{'gender': row['gender'], 'count': row['count']} for row in gender_stats] if gender_stats else [],
            'programme': [{'programme': row['programme'], 'count': row['count']} for row in programme_stats] if programme_stats else [],
            'department': [{'department': row['department'], 'count': row['count']} for row in department_stats] if department_stats else [],
            'appointment_status': [{'status': row['status'], 'count': row['count']} for row in appointment_status_stats] if appointment_status_stats else [],
            'appointment_timeline': [{'month': row['month'], 'count': row['count']} for row in appointment_timeline] if appointment_timeline else [],
            'session_timeline': [{'month': row['month'], 'count': row['count']} for row in session_timeline] if session_timeline else [],
            'session_type': [{'session_type': row['session_type'], 'count': row['count']} for row in session_type_stats] if session_type_stats else [],
            'age_distribution': [{'age_group': row['age_group'], 'count': row['count']} for row in age_distribution] if age_distribution else [],
            'top_counsellors': [{'name': row['name'], 'count': row['appointment_count']} for row in top_counsellors] if top_counsellors else [],
            'new_students_timeline': [{'month': row['month'], 'count': row['count']} for row in new_students_timeline] if new_students_timeline else []
        }
        
        return render_template('statistics.html', stats_data=stats_data)
    
    except Exception as e:
        print(f"[STATISTICS] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading statistics: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Add error handler for 500 errors - display them properly
@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_trace = traceback.format_exc()
    print(f"[ERROR 500] {error}")
    print(f"[ERROR 500] Traceback:\n{error_trace}")
    
    # Try to log to file if running as EXE
    try:
        if getattr(sys, 'frozen', False):
            try:
                base_path = os.path.dirname(sys.executable)
            except:
                base_path = os.path.dirname(os.path.abspath(__file__))
            error_log_path = os.path.join(base_path, 'error_log.txt')
            with open(error_log_path, 'a') as f:
                f.write(f"\n=== ERROR {datetime.now()} ===\n")
                f.write(f"{error}\n")
                f.write(f"{error_trace}\n")
                f.write("=" * 50 + "\n")
            print(f"[ERROR] Details logged to: {error_log_path}")
    except:
        pass
    
    return '''
    <html>
    <head><title>Internal Server Error</title></head>
    <body style="font-family: sans-serif; padding: 2rem; line-height: 1.6;">
        <h1 style="color: #dc3545;">Internal Server Error</h1>
        <p>The server encountered an error while processing your request.</p>
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 4px; border: 1px solid #dee2e6; margin: 1rem 0;">
            <code>''' + str(error) + '''</code>
        </div>
        <p><a href="/welcome" style="display: inline-block; background: #0d6efd; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px;">Return to Login</a></p>
    </body>
    </html>
    ''', 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors (like 404, 405, etc.) so Flask handles them normally
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
        
    # For actual unhandled code exceptions, log and return 500
    import traceback
    error_trace = traceback.format_exc()
    print(f"[UNHANDLED ERROR] {e}")
    print(f"[UNHANDLED ERROR] Traceback:\n{error_trace}")
    return internal_error(e)

if __name__ == '__main__':
    # Initialize database FIRST before anything else
    print("Initializing database...")
    try:
        # Force database initialization at startup
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
        except:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'counseling.db')
        
        # Check and initialize
import threading
import time

def run_auto_sync_loop():
    """Background thread to auto-sync every 10 seconds"""
    print("--- Auto-Sync Service Started ---")
    while True:
        try:
            # Check if sync is enabled and peer IP is set
            config = node_config.load_config()
            peer_ip = config.get('peer_ip')  
            if peer_ip:
                # Trigger sync silently
                # We use a slight delay or check to avoid spamming if offline
                result = trigger_sync()
                if result.get('status') == 'success' and result.get('count', 0) > 0:
                    print(f"[AUTO-SYNC] Synced {result['count']} records.")
            
        except Exception as e:
            print(f"[AUTO-SYNC] Error: {e}")
        
        # Sleep for 10 seconds before next sync attempt
        time.sleep(10)

if __name__ == '__main__':
    # Initialize database FIRST before anything else
    print("Initializing database...")
    try:
        # Force database initialization at startup
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
        except:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(base_path, 'counseling.db')
        
        # Check and initialize
        if not os.path.exists(db_path):
            print(f"Database not found, creating at: {db_path}")
            import db_setup
            db_setup.init_db()
        else:
            # Verify Appointment table exists
            test_conn = sqlite3.connect(db_path)
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Appointment'")
            if not cursor.fetchone():
                print("Appointment table missing, reinitializing database...")
                test_conn.close()
                import db_setup
                db_setup.init_db()
            else:
                test_conn.close()
                print("Database check passed - Appointment table exists")
    except Exception as e:
        print(f"WARNING: Database initialization issue: {e}")
        print("Attempting to continue anyway...")
    
    # Check if port 5000 is already in use and kill the process if needed
    import socket
    import subprocess
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 5000))
        sock.close()
    except OSError as e:
        if e.errno == 10048 or (hasattr(e, 'winerror') and e.winerror == 10048):  # Port already in use
            print("WARNING: Port 5000 is already in use!")
            print("Attempting to kill the process using port 5000...")
            try:
                # Find process using port 5000
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if ':5000' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            print(f"Found process {pid} using port 5000. Killing it...")
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True, timeout=5)
                            import time
                            time.sleep(1)  # Wait a bit for port to be released
                # Try binding again
                try:
                    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock2.bind(('127.0.0.1', 5000))
                    sock2.close()
                    print("Port 5000 is now available!")
                except:
                    print("ERROR: Could not free port 5000.")
                    print("Please manually close other instances or restart your computer.")
                    is_exe = getattr(sys, 'frozen', False)
                    if not is_exe:
                        input("Press Enter to exit...")
                    sys.exit(1)
            except Exception as kill_error:
                print(f"Could not kill process: {kill_error}")
                print("Please manually close other instances.")
                is_exe = getattr(sys, 'frozen', False)
                if not is_exe:
                    input("Press Enter to exit...")
                sys.exit(1)
    
    # Start Auto-Sync Thread
    sync_thread = threading.Thread(target=run_auto_sync_loop, daemon=True)
    sync_thread.start()

    # Log available routes for debugging
    print('=' * 60)
    print('AAMUSTED Counselling Management System')
    print('=' * 60)
    print('Starting server on http://127.0.0.1:5000')
    print('Registered routes:')
    for rule in app.url_map.iter_rules():
        if rule.endpoint not in ['static']:
            print(f"  - {rule.endpoint}: {rule}")
    print('=' * 60)
    print()
    
    # For EXE, don't use debug mode and open browser automatically
    import webbrowser
    import threading
    
    def open_browser():
        import time
        time.sleep(2.5)  # Wait longer for server to fully start
        try:
            # Try to open browser
            webbrowser.open('http://127.0.0.1:5000')
            print("Browser opened automatically!")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please manually open: http://localhost:5000")
    
    # Open browser automatically (only if not in debug mode)
    is_exe = getattr(sys, 'frozen', False)
    if is_exe:
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        print("Server starting... Browser will open automatically.")
    else:
        print("Starting in development mode...")
        print("Local access: http://localhost:5000")
        print("Network access: http://<your-ip-address>:5000")
    
    print()
    
    try:
        # Run app (debug=False for production EXE)
        app.run(debug=not getattr(sys, 'frozen', False), host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)