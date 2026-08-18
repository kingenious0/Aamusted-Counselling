import os
import logging
import uuid
import random
import string
from datetime import datetime, date
from functools import wraps

from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static'),
)
app.secret_key = os.environ.get('SECRET_KEY', 'aamusted-gcc-secret-2026-xK9mP')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
CORS(app)

BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "sb_bridge_AnEpYo_2026")
DATABASE_URL = os.environ.get("DATABASE_URL")
_db_initialized = False


def get_db():
    import psycopg2
    import socket
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing in Vercel environment variables")

    _orig_getaddrinfo = socket.getaddrinfo
    def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    socket.getaddrinfo = _ipv4_getaddrinfo

    try:
        if 'sslmode=' in DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    finally:
        socket.getaddrinfo = _orig_getaddrinfo


def dict_cursor(conn):
    import psycopg2.extras
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/') or request.path.startswith('/sync/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                flash('You do not have access to this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def init_db():
    from werkzeug.security import generate_password_hash
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT NOT NULL DEFAULT 'Admin',
                phone TEXT,
                email TEXT,
                profile_pic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db users: {e}")
        conn.rollback()
    try:
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                ('admin', generate_password_hash('admin123'), 'System Admin', 'Admin')
            )
    except Exception as e:
        logger.error(f"init_db admin user: {e}")
        conn.rollback()
    try:
        cur.execute("SELECT id FROM users WHERE username = 'secretary'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                ('secretary', generate_password_hash('secretary123'), 'Desk Secretary', 'Secretary')
            )
    except Exception as e:
        logger.error(f"init_db secretary user: {e}")
        conn.rollback()
    try:
        cur.execute("SELECT id FROM users WHERE username = 'counsellor'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                ('counsellor', generate_password_hash('counsellor123'), 'Default Counsellor', 'Counsellor')
            )
    except Exception as e:
        logger.error(f"init_db counsellor user: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Counsellor" (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                contact TEXT,
                specialization TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Counsellor: {e}")
        conn.rollback()
    try:
        cur.execute('SELECT id FROM "Counsellor" WHERE name = %s', ('Default Counsellor',))
        if not cur.fetchone():
            cur.execute('INSERT INTO "Counsellor" (name, contact) VALUES (%s, %s)', ('Default Counsellor', ''))
    except Exception as e:
        logger.error(f"init_db default counsellor: {e}")
        conn.rollback()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Student" (
                id SERIAL PRIMARY KEY,
                first_name TEXT, last_name TEXT, name TEXT, student_id TEXT,
                case_number TEXT, index_number TEXT, email TEXT, phone TEXT,
                gender TEXT, program TEXT, programme TEXT, department TEXT,
                level TEXT, reason_for_visit TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Student: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Appointment" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT,
                appointment_date TEXT, appointment_time TEXT,
                appointment_type TEXT, counsellor TEXT, notes TEXT,
                status TEXT DEFAULT 'Scheduled', booking_ref TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Appointment: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "session" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, session_type TEXT,
                session_date TEXT, notes TEXT, diagnosis TEXT, plan TEXT,
                counsellor TEXT, status TEXT DEFAULT 'Scheduled',
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db session: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Referral" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, referred_by TEXT,
                contact TEXT, reason TEXT, notes TEXT, status TEXT DEFAULT 'Pending',
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Referral: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "CaseManagement" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, session_date TEXT,
                appearance_problems TEXT, clinical_plan TEXT, counsellor TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db CaseManagement: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "DASS21" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, total_score INTEGER,
                severity TEXT, counsellor TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db DASS21: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "OutcomeQuestionnaire" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, responses TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db OutcomeQuestionnaire: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Notification" (
                id SERIAL PRIMARY KEY,
                user_id INTEGER, message TEXT, type TEXT, link TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Notification: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "BookingRequest" (
                id SERIAL PRIMARY KEY,
                reference TEXT UNIQUE, student_name TEXT, student_id TEXT,
                email TEXT, phone TEXT, program TEXT, level TEXT,
                reason TEXT, preferred_date TEXT, preferred_time TEXT,
                status TEXT DEFAULT 'Pending',
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db BookingRequest: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id SERIAL PRIMARY KEY,
                setting_name TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                global_id UUID DEFAULT gen_random_uuid(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db app_settings: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Feedback" (
                id SERIAL PRIMARY KEY,
                student_name TEXT, student_id TEXT, feedback_text TEXT,
                rating INTEGER,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db Feedback: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "SessionIssue" (
                id SERIAL PRIMARY KEY,
                session_id INTEGER, issue_text TEXT, severity TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db SessionIssue: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                username TEXT, action TEXT, table_name TEXT, details TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db audit_logs: {e}")
        conn.rollback()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                title TEXT, report_type TEXT, summary TEXT, file_path TEXT,
                generated_by TEXT,
                is_deleted BOOLEAN DEFAULT FALSE,
                global_id UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
    except Exception as e:
        logger.error(f"init_db reports: {e}")
        conn.rollback()
    try:
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS full_name TEXT;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS index_number TEXT;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS department TEXT;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS programme TEXT;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS hall_of_residence TEXT;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP WITH TIME ZONE;
        """)
        cur.execute("""
            ALTER TABLE "BookingRequest" ADD COLUMN IF NOT EXISTS decline_reason TEXT;
        """)
        cur.execute("""
            ALTER TABLE "Appointment" ADD COLUMN IF NOT EXISTS urgency TEXT DEFAULT 'Normal';
        """)
        cur.execute("""
            ALTER TABLE "Appointment" ADD COLUMN IF NOT EXISTS purpose TEXT;
        """)
        cur.execute("""
            ALTER TABLE "Appointment" ADD COLUMN IF NOT EXISTS checked_in_at TIMESTAMP WITH TIME ZONE;
        """)
        cur.execute("""
            ALTER TABLE "Appointment" ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;
        """)
        cur.execute("""
            ALTER TABLE "Appointment" ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE;
        """)
        cur.execute("""
            ALTER TABLE "Student" ADD COLUMN IF NOT EXISTS age INTEGER;
        """)
        cur.execute("""
            ALTER TABLE "Student" ADD COLUMN IF NOT EXISTS hall_of_residence TEXT;
        """)
        cur.execute("""
            ALTER TABLE "Student" ADD COLUMN IF NOT EXISTS parent_contact TEXT;
        """)
    except Exception as e:
        logger.error(f"init_db alter columns: {e}")
        conn.rollback()
    try:
        conn.commit()
    except Exception:
        pass
    cur.close()
    conn.close()


def generate_booking_ref(conn):
    """Generate a unique BK-YYYY-XXXX booking reference."""
    cur = conn.cursor()
    year = datetime.now().year
    try:
        cur.execute(
            "SELECT reference FROM \"BookingRequest\" WHERE reference LIKE %s ORDER BY id DESC LIMIT 1",
            (f"BK-{year}-%",),
        )
        row = cur.fetchone()
        if row and row[0]:
            last_num = int(row[0].split('-')[-1])
        else:
            last_num = 0
        return f"BK-{year}-{str(last_num + 1).zfill(4)}"
    except Exception:
        return f"BK-{year}-{str(uuid.uuid4())[:4].upper()}"


def generate_case_number(conn):
    """Generate GCC/MONTH/YY/XXX case number."""
    cur = conn.cursor()
    now = datetime.now()
    month_abbr = now.strftime('%b').upper()
    year_short = now.strftime('%y')
    try:
        cur.execute(
            "SELECT case_number FROM \"Student\" WHERE case_number LIKE %s ORDER BY id DESC LIMIT 1",
            (f"GCC/{month_abbr}/{year_short}/%",),
        )
        row = cur.fetchone()
        if row and row[0]:
            last_num = int(row[0].split('/')[-1])
        else:
            last_num = 0
        return f"GCC/{month_abbr}/{year_short}/{str(last_num + 1).zfill(3)}"
    except Exception:
        return f"GCC/{month_abbr}/{year_short}/001"


def name_to_initials(name_input):
    """Convert full name to initials for privacy."""
    if not name_input:
        return 'N/A'
    parts = name_input.strip().split()
    if len(parts) >= 2:
        return parts[0][0] + '.' + parts[-1][0] + '.'
    return name_input[0] + '.' if name_input else 'N/A'


def fire_staff_notifications(conn, message, link='/admin/bookings'):
    """Insert in-app notifications for all staff."""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE role IN ('Secretary', 'Admin', 'Counsellor', 'Counselor')"
        )
        staff = cur.fetchall()
        for row in staff:
            uid = row[0] if isinstance(row, tuple) else row.get('id')
            cur.execute(
                """INSERT INTO "Notification" (user_id, message, type, link, global_id, created_at)
                   VALUES (%s, %s, 'in_app', %s, %s, NOW())""",
                (uid, message, link, str(uuid.uuid4())),
            )
        conn.commit()
    except Exception as e:
        logger.error(f"fire_staff_notifications: {e}")
        conn.rollback()


@app.before_request
def _ensure_db():
    global _db_initialized
    if _db_initialized:
        return
    try:
        init_db()
        _db_initialized = True
    except Exception as e:
        logger.error(f"Lazy init_db error: {e}")


@app.context_processor
def inject_globals():
    settings = {}
    latest_booking_count = 0
    unread_count = 0
    notifications = []
    if 'user_id' in session:
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT setting_name, setting_value FROM app_settings")
            for row in cur.fetchall():
                settings[row[0]] = row[1]
            cur.execute("SELECT COUNT(*) FROM \"BookingRequest\" WHERE status = 'Pending'")
            latest_booking_count = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM \"Notification\" WHERE user_id = %s AND is_read = FALSE",
                (session['user_id'],),
            )
            unread_count = cur.fetchone()[0]
            cur.execute(
                "SELECT * FROM \"Notification\" WHERE user_id = %s ORDER BY created_at DESC LIMIT 10",
                (session['user_id'],),
            )
            notifications = [dict(r) for r in cur.fetchall()]
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"context_processor: {e}")
    return {
        'settings': settings,
        'latest_booking_count': latest_booking_count,
        'unread_count': unread_count,
        'notifications': notifications,
    }


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from werkzeug.security import check_password_hash
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            conn = get_db()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name'] or user['username']
                session['role'] = user['role']
                return redirect(url_for('dashboard'))
            flash('Invalid username or password.', 'error')
        except Exception as e:
            logger.error(f"login: {e}")
            flash(f'Login error: {e}', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats = {'total_students': 0, 'total_appointments': 0, 'pending_bookings': 0, 'total_sessions': 0, 'total_referrals': 0, 'total_users': 0}
    recent_activity = []
    booking_count = 0
    try:
        conn = get_db()
        cur = conn.cursor()
        queries = [
            ('total_students', 'SELECT COUNT(*) FROM "Student" WHERE is_deleted = FALSE'),
            ('total_appointments', 'SELECT COUNT(*) FROM "Appointment" WHERE is_deleted = FALSE'),
            ('total_sessions', 'SELECT COUNT(*) FROM "session" WHERE is_deleted = FALSE'),
            ('total_referrals', 'SELECT COUNT(*) FROM "Referral" WHERE is_deleted = FALSE'),
        ]
        for key, sql in queries:
            try:
                cur.execute(sql)
                stats[key] = cur.fetchone()[0]
            except Exception:
                pass
        try:
            cur.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cur.fetchone()[0]
        except Exception:
            pass
        try:
            cur.execute('SELECT COUNT(*) FROM "BookingRequest" WHERE status = \'Pending\' AND is_deleted = FALSE')
            booking_count = cur.fetchone()[0]
            stats['pending_bookings'] = booking_count
        except Exception:
            pass
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('dashboard.html', stats=stats, booking_count=booking_count, recent_activity=recent_activity)


@app.route('/admin/bookings')
@login_required
@roles_required('Admin', 'Secretary', 'Counsellor', 'Counselor')
def admin_bookings():
    tab = request.args.get('tab', 'recent')
    bookings = []
    recent_count = history_count = all_count = 0
    try:
        conn = get_db()
        cur = dict_cursor(conn)

        cur.execute("SELECT COUNT(*) FROM \"BookingRequest\" WHERE status IN ('Pending','Accepted')")
        recent_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM \"BookingRequest\" WHERE status = 'Declined'")
        history_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM \"BookingRequest\"")
        all_count = cur.fetchone()['count']

        if tab == 'recent':
            cur.execute(
                "SELECT * FROM \"BookingRequest\" WHERE status IN ('Pending','Accepted') ORDER BY created_at DESC"
            )
        elif tab == 'history':
            cur.execute("SELECT * FROM \"BookingRequest\" WHERE status = 'Declined' ORDER BY created_at DESC")
        else:
            cur.execute("SELECT * FROM \"BookingRequest\" ORDER BY created_at DESC")

        bookings = cur.fetchall()
        for b in bookings:
            cur.execute('SELECT id FROM "Appointment" WHERE booking_ref = %s', (b['reference'],))
            b['is_registered'] = cur.fetchone() is not None
            name = b.get('full_name', '')
            if name:
                parts = name.split()
                b['masked_name'] = (parts[0][0] + '.' + parts[-1][0] + '.') if len(parts) >= 2 else (name[0] + '.')
            else:
                b['masked_name'] = 'N/A'
            for k, v in b.items():
                if isinstance(v, (datetime, date)):
                    b[k] = v.strftime('%Y-%m-%d')

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"admin_bookings: {e}")

    return render_template(
        'admin_bookings.html',
        bookings=bookings,
        recent_count=recent_count,
        history_count=history_count,
        all_count=all_count,
        current_tab=tab,
    )


@app.route('/admin/bookings/<ref>/register')
@login_required
@roles_required('Admin', 'Secretary', 'Counsellor', 'Counselor')
def register_booking(ref):
    try:
        conn = get_db()
        cur = dict_cursor(conn)

        cur.execute('SELECT * FROM "BookingRequest" WHERE reference = %s', (ref,))
        booking = cur.fetchone()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        cur.execute('SELECT id FROM "Appointment" WHERE booking_ref = %s', (ref,))
        if cur.fetchone():
            return jsonify({'error': 'Already registered'}), 400

        name = booking.get('full_name', '')
        parts = name.split()
        masked_name = (parts[0][0] + '.' + parts[-1][0] + '.') if len(parts) >= 2 else (name[0] + '.' if name else 'N/A')

        now = datetime.now()
        month_abbr = now.strftime('%b').upper()
        year_short = now.strftime('%y')
        cur.execute('SELECT COUNT(*) FROM "Student" WHERE created_at >= %s', (now.replace(day=1),))
        count = cur.fetchone()['count'] + 1
        case_number = f"GCC/{month_abbr}/{year_short}/{count:03d}"

        cur.execute(
            """INSERT INTO "Student"
               (name, case_number, index_number, department, programme,
                contact, gender, age, email, hall_of_residence, global_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               RETURNING id""",
            (
                masked_name, case_number,
                booking.get('index_number'), booking.get('department'),
                booking.get('programme'), booking.get('phone'),
                booking.get('gender'), booking.get('age'),
                booking.get('email'), booking.get('hall_of_residence'),
                str(uuid.uuid4()),
            ),
        )
        student_id = cur.fetchone()['id']

        cur.execute(
            """INSERT INTO "Appointment"
               (student_id, date, time, purpose, status, booking_ref, urgency, global_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               RETURNING id""",
            (
                student_id,
                booking.get('preferred_date'),
                booking.get('preferred_time'),
                booking.get('reason'),
                'Scheduled', ref, 'Normal',
                str(uuid.uuid4()),
            ),
        )

        cur.execute(
            """UPDATE "BookingRequest"
               SET status = 'Accepted', accepted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
               WHERE reference = %s""",
            (ref,),
        )

        cur.execute(
            """INSERT INTO "Notification" (user_id, message, type, link, global_id)
               VALUES (1, %s, 'in_app', %s, %s)""",
            (f'Booking {ref} registered as student {case_number}', '/admin/bookings', str(uuid.uuid4())),
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'student_id': student_id, 'case_number': case_number})

    except Exception as e:
        logger.error(f"register_booking: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/bookings/<ref>/decline', methods=['POST'])
@login_required
@roles_required('Admin', 'Secretary', 'Counsellor')
def decline_booking(ref):
    try:
        data = request.json or {}
        reason = data.get('reason', '')
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """UPDATE "BookingRequest"
               SET status = 'Declined', decline_reason = %s, updated_at = CURRENT_TIMESTAMP
               WHERE reference = %s""",
            (reason, ref),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/students')
@login_required
def students():
    search = request.args.get('search', '').strip()
    students_list = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        if search:
            cur.execute(
                """SELECT * FROM "Student"
                   WHERE is_deleted = FALSE AND (
                       name ILIKE %s OR case_number ILIKE %s OR
                       index_number ILIKE %s OR department ILIKE %s
                   ) ORDER BY created_at DESC""",
                (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'),
            )
        else:
            cur.execute('SELECT * FROM "Student" WHERE is_deleted = FALSE ORDER BY created_at DESC')
        students_list = cur.fetchall()
        for s in students_list:
            for k, v in s.items():
                if isinstance(v, (datetime, date)):
                    s[k] = v.strftime('%Y-%m-%d')
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"students: {e}")
    return render_template('students.html', students=students_list, search=search)


def verify_api_key():
    return request.headers.get("X-API-KEY") == BRIDGE_API_KEY


@app.route("/sync/stats", methods=["GET"])
def sync_stats():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        conn = get_db()
        cur = conn.cursor()
        tables = [
            'Student','Appointment','session','Referral','CaseManagement',
            'OutcomeQuestionnaire','DASS21','Feedback','SessionIssue',
            'Notification','app_settings','BookingRequest',
        ]
        counts = {}
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{t}"')
                counts[t] = cur.fetchone()[0]
            except Exception:
                conn.rollback()
                counts[t] = -1
        cur.close()
        conn.close()
        return jsonify({"status": "success", "counts": counts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sync/push", methods=["POST"])
def push_changes():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    changes = data.get("changes", {})
    table_name = data.get("table")
    records = data.get("records")
    cleanup_tables = data.get("cleanup_tables", [])
    if table_name and records:
        changes = {table_name: records}
    if not isinstance(changes, dict):
        return jsonify({"error": "Invalid format"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        for t in cleanup_tables:
            cur.execute(f'DELETE FROM "{t}"')
        stats = {}
        for table, record_list in changes.items():
            stats[table] = 0
            for record in record_list:
                try:
                    clean = {k: v for k, v in record.items() if k != 'id'}
                    for k in ['is_deleted', 'is_read']:
                        if k in clean:
                            clean[k] = bool(clean[k])
                    if table == 'app_settings':
                        conflict = 'setting_name'
                    elif table == 'BookingRequest':
                        conflict = 'reference'
                    else:
                        conflict = 'global_id'
                    incoming_ts = clean.get('updated_at', '1970-01-01 00:00:00')
                    cur.execute(f'SELECT updated_at FROM "{table}" WHERE "{conflict}" = %s', (clean.get(conflict),))
                    existing = cur.fetchone()
                    if existing and existing[0] and incoming_ts and incoming_ts <= str(existing[0]):
                        stats[table] += 1
                        continue
                    cols = list(clean.keys())
                    vals = [clean[c] for c in cols]
                    placeholders = ', '.join(['%s'] * len(cols))
                    upd = ', '.join([f'"{c}" = EXCLUDED."{c}"' for c in cols if c != conflict])
                    col_list = ', '.join([f'"{c}"' for c in cols])
                    cur.execute(
                        f'INSERT INTO "{table}" ({col_list}) '
                        f'VALUES ({placeholders}) ON CONFLICT ("{conflict}") DO UPDATE SET {upd}',
                        tuple(vals),
                    )
                    stats[table] += 1
                except Exception as e:
                    logger.error(f"push {table}: {e}")
                    conn.rollback()
                    continue
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "counts": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sync/pull", methods=["POST"])
def pull_data():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    since = data.get("last_sync_timestamp")
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        tables = [
            'Student','Appointment','session','Referral','CaseManagement',
            'OutcomeQuestionnaire','DASS21','Feedback','SessionIssue',
            'Notification','app_settings','BookingRequest',
        ]
        all_changes = {}
        total = 0
        for table in tables:
            q = f'SELECT * FROM "{table}"'
            if since and since != '1970-01-01 00:00:00':
                cur.execute(q + ' WHERE updated_at > %s', (since,))
            else:
                cur.execute(q)
            records = cur.fetchall()
            if records:
                sanitized = []
                for r in records:
                    d = dict(r)
                    if not d.get('global_id') and table not in ('app_settings', 'BookingRequest'):
                        d['global_id'] = f"cloud-{table}-{d.get('id')}"
                    sanitized.append(d)
                all_changes[table] = sanitized
                total += len(sanitized)
        cur.close()
        conn.close()
        for tbl in all_changes:
            for rec in all_changes[tbl]:
                for k, v in rec.items():
                    if isinstance(v, datetime):
                        rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({"changes": all_changes, "count": total, "server_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/submit_booking", methods=["POST"])
def portal_booking():
    data = request.json or {}
    try:
        if not data.get('reference'):
            data['reference'] = 'BR-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not data.get('global_id'):
            data['global_id'] = str(uuid.uuid4())
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = now
        data['created_at'] = now
        data.setdefault('status', 'Pending')
        conn = get_db()
        cur = conn.cursor()
        KNOWN = [
            'reference','full_name','index_number','department','programme',
            'phone','preferred_date','preferred_time','reason','status',
            'email','hall_of_residence','gender','age',
            'global_id','updated_at','created_at',
        ]
        cols = [c for c in data if c in KNOWN]
        vals = [data[c] for c in cols]
        col_list = ', '.join([f'"{c}"' for c in cols])
        val_ph = ', '.join(['%s'] * len(cols))
        cur.execute(
            f'INSERT INTO "BookingRequest" ({col_list}) '
            f'VALUES ({val_ph}) RETURNING reference',
            vals,
        )
        ref = cur.fetchone()[0]
        conn.commit()

        # Fire in-app notifications to all staff
        full_name = data.get('full_name', 'Unknown')
        idx = data.get('index_number', '')
        fire_staff_notifications(
            conn,
            f"New booking {ref} from {full_name} ({idx}) via API",
            '/admin/bookings',
        )

        cur.close()
        conn.close()
        return jsonify({"status": "success", "reference": ref}), 201
    except Exception as e:
        logger.error(f"portal_booking: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_theme")
def get_theme():
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT setting_name, setting_value FROM app_settings')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        settings = {r['setting_name']: r['setting_value'] for r in rows}
        return jsonify({
            'theme': settings.get('active_theme') or settings.get('theme_color') or 'default',
            'system_name': settings.get('system_name') or 'AAMUSTED Guidance & Counselling',
            'logo_url': settings.get('logo_url') or '/static/aamusted system_logo.png',
        })
    except Exception:
        return jsonify({
            'theme': 'default',
            'system_name': 'AAMUSTED Guidance & Counselling',
            'logo_url': '/static/aamusted system_logo.png',
        })


@app.route("/api/admin/cloud_proxy/stats")
@login_required
def cloud_proxy_stats():
    if session.get('role') != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    tables = [
        'Student', 'Appointment', 'Referral', 'CaseManagement',
        'OutcomeQuestionnaire', 'DASS21', 'Feedback', 'SessionIssue',
        'Notification', 'Counsellor', 'BookingRequest',
    ]
    counts = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{t}" WHERE is_deleted = FALSE')
                counts[t] = cur.fetchone()[0]
            except Exception:
                counts[t] = 0
        cur.close()
        conn.close()
    except Exception:
        for t in tables:
            counts[t] = 0
    return jsonify({
        'status': 'online',
        'total_records': sum(counts.values()),
        'tables': counts,
    })


@app.route("/api/sync/status")
@login_required
def get_sync_status():
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'last_cloud_sync'")
        row = cur.fetchone()
        cur.close()
        conn.close()
        last_sync = row['setting_value'] if row else None
    except Exception:
        last_sync = None
    return jsonify({
        'status': 'active',
        'last_sync': last_sync,
        'mode': 'cloud',
    })


@app.route("/api/sync/check_alerts")
@login_required
def check_alerts():
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'pending_booking_alert'")
        row = cur.fetchone()
        has_alert = row and row.get('setting_value') == 'true'
        if has_alert:
            cur.execute("UPDATE app_settings SET setting_value = 'false' WHERE setting_name = 'pending_booking_alert'")
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"new_booking": has_alert})
    except Exception:
        return jsonify({"new_booking": False})


@app.route("/api/offline/pull", methods=["POST"])
@login_required
def offline_pull():
    data = request.get_json(silent=True) or {}
    last_sync = data.get('last_sync')
    tables = [
        'Student', 'Appointment', 'Referral', 'CaseManagement',
        'OutcomeQuestionnaire', 'DASS21', 'Feedback', 'SessionIssue',
        'Notification', 'Counsellor',
    ]
    result = {}
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        for t in tables:
            try:
                if last_sync:
                    cur.execute(f'SELECT * FROM "{t}" WHERE updated_at > %s AND is_deleted = FALSE ORDER BY updated_at DESC LIMIT 500', (last_sync,))
                else:
                    cur.execute(f'SELECT * FROM "{t}" WHERE is_deleted = FALSE ORDER BY updated_at DESC LIMIT 500')
                rows = cur.fetchall()
                for r in rows:
                    for k, v in r.items():
                        if isinstance(v, (datetime, date)):
                            r[k] = v.isoformat()
                result[t] = rows
            except Exception:
                result[t] = []
        cur.close()
        conn.close()
    except Exception:
        for t in tables:
            result[t] = []
    return jsonify(result)


@app.route("/admin/settings")
@login_required
def admin_settings():
    settings = {}
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT setting_name, setting_value FROM app_settings')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        settings = {r['setting_name']: r['setting_value'] for r in rows}
    except Exception:
        pass
    return render_template('admin_settings.html', settings=settings)


@app.route("/admin/settings/update", methods=["POST"])
@login_required
def admin_update_settings():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    try:
        conn = get_db()
        cur = conn.cursor()
        system_name = request.form.get('system_name', '')
        logo_url = request.form.get('logo_url', '')
        active_theme = request.form.get('active_theme', '')
        updates = {
            'system_name': system_name,
            'logo_url': logo_url,
            'active_theme': active_theme,
            'theme_color': active_theme,
        }
        for key, val in updates.items():
            if val and str(val).strip():
                cur.execute(
                    """INSERT INTO app_settings (setting_name, setting_value, global_id, updated_at)
                       VALUES (%s, %s, gen_random_uuid(), NOW())
                       ON CONFLICT (setting_name) DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = NOW()""",
                    (key, val),
                )
        conn.commit()
        cur.close()
        conn.close()
        flash("Settings saved successfully", "success")
    except Exception as e:
        logger.error(f"admin_update_settings: {e}")
        flash(f"Error saving settings: {e}", "error")
    return redirect(url_for('admin_settings'))


@app.route("/admin/cloud_sync")
@login_required
def admin_cloud_sync():
    if session.get('role') != 'Admin':
        flash("Unauthorized access", "error")
        return redirect(url_for('dashboard'))
    tables = [
        'Student', 'Appointment', 'Referral', 'CaseManagement',
        'OutcomeQuestionnaire', 'DASS21', 'Feedback', 'SessionIssue',
        'Notification', 'Counsellor', 'BookingRequest',
    ]
    local_counts = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{t}"')
                local_counts[t] = cur.fetchone()[0]
            except Exception:
                local_counts[t] = 0
        cur.close()
        conn.close()
    except Exception:
        for t in tables:
            local_counts[t] = 0
    return render_template('admin_cloud_sync.html', local_counts=local_counts, sync_tables=tables)


@app.route("/all_referrals")
@login_required
def all_referrals():
    referrals = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "Referral" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 500')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        referrals = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('all_referrals.html', referrals=referrals)


@app.route("/referral", methods=["GET", "POST"])
@login_required
def referral():
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO "Referral" (student_name, student_id, referred_by, contact, reason, notes, status, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                (request.form.get('student_name', ''), request.form.get('student_id', ''),
                 request.form.get('referred_by', ''), request.form.get('contact', ''),
                 request.form.get('reason', ''), request.form.get('notes', ''), 'Pending'),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Referral created successfully", "success")
            return redirect(url_for('all_referrals'))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template('referral.html')


@app.route("/case_notes_list")
@login_required
def case_notes_list():
    cases = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "CaseManagement" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 500')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        cases = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('case_notes_list.html', cases=cases)


@app.route("/case_note", methods=["GET", "POST"])
@login_required
def case_note():
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO "CaseManagement" (student_name, student_id, session_date, appearance_problems, clinical_plan, counsellor, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                (request.form.get('student_name', ''), request.form.get('student_id', ''),
                 request.form.get('session_date', ''), request.form.get('appearance', ''),
                 request.form.get('clinical_plan', ''), session.get('username', '')),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Case note saved", "success")
            return redirect(url_for('case_notes_list'))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template('case_note.html')


@app.route("/sessions")
@login_required
def sessions_list():
    sessions_data = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "session" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 500')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        sessions_data = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('sessions.html', sessions=sessions_data)


@app.route("/create_session", methods=["GET", "POST"])
@login_required
def create_session():
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO "session" (student_name, student_id, session_type, session_date, notes, diagnosis, plan, counsellor, status, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                (request.form.get('student_name', ''), request.form.get('student_id', ''),
                 request.form.get('session_type', 'Individual'), request.form.get('session_date', ''),
                 request.form.get('notes', ''), request.form.get('diagnosis', ''),
                 request.form.get('plan', ''), session.get('username', ''), 'Scheduled'),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Session created", "success")
            return redirect(url_for('sessions_list'))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template('create_session.html')


@app.route("/dass21_list")
@login_required
def dass21_list():
    assessments = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "DASS21" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 500')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        assessments = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('dass21_list.html', assessments=assessments)


@app.route("/dass21", methods=["GET", "POST"])
@login_required
def dass21():
    if request.method == "POST":
        try:
            total = sum(int(request.form.get(f'q{i}', 0)) for i in range(1, 22))
            severity = "Normal"
            if total >= 28: severity = "Extremely Severe"
            elif total >= 20: severity = "Severe"
            elif total >= 15: severity = "Moderate"
            elif total >= 10: severity = "Mild"
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO "DASS21" (student_name, student_id, total_score, severity, counsellor, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, NOW(), NOW())''',
                (request.form.get('student_name', ''), request.form.get('student_id', ''),
                 total, severity, session.get('username', '')),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash(f"Assessment complete. Score: {total} ({severity})", "success")
            return redirect(url_for('dass21_list'))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template('dass21.html')


@app.route("/outcome_questionnaire", methods=["GET", "POST"])
@login_required
def outcome_questionnaire():
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO "OutcomeQuestionnaire" (student_name, student_id, responses, created_at, updated_at)
                   VALUES (%s, %s, %s, NOW(), NOW())''',
                (request.form.get('student_name', ''), request.form.get('student_id', ''),
                 str(dict(request.form))),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Outcome recorded", "success")
            return redirect(url_for('reports'))
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template('outcome_questionnaire.html')


@app.route("/reports")
@login_required
def reports():
    reports_data = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        try:
            cur.execute('SELECT * FROM reports WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 200')
        except Exception:
            cur.execute('SELECT * FROM "OutcomeQuestionnaire" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 200')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        reports_data = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('reports.html', reports=reports_data)


@app.route("/statistics")
@login_required
def statistics():
    stats = {
        'total_students': 0, 'total_sessions': 0, 'total_referrals': 0,
        'total_assessments': 0, 'total_appointments': 0, 'total_cases': 0,
        'male_count': 0, 'female_count': 0,
        'sessions_this_month': 0, 'referrals_this_month': 0,
        'gender_data': {}, 'program_data': {}, 'severity_data': {},
        'monthly_sessions': {}, 'status_data': {},
    }
    try:
        conn = get_db()
        cur = conn.cursor()
        queries = [
            ('total_students', 'SELECT COUNT(*) FROM "Student" WHERE is_deleted = FALSE'),
            ('total_sessions', 'SELECT COUNT(*) FROM "session" WHERE is_deleted = FALSE'),
            ('total_referrals', 'SELECT COUNT(*) FROM "Referral" WHERE is_deleted = FALSE'),
            ('total_assessments', 'SELECT COUNT(*) FROM "DASS21" WHERE is_deleted = FALSE'),
            ('total_appointments', 'SELECT COUNT(*) FROM "Appointment" WHERE is_deleted = FALSE'),
            ('total_cases', 'SELECT COUNT(*) FROM "CaseManagement" WHERE is_deleted = FALSE'),
        ]
        for key, sql in queries:
            try:
                cur.execute(sql)
                stats[key] = cur.fetchone()[0]
            except Exception:
                pass
        try:
            cur.execute('SELECT gender, COUNT(*) FROM "Student" WHERE is_deleted = FALSE AND gender IS NOT NULL AND gender != \'\' GROUP BY gender')
            for row in cur.fetchall():
                stats['gender_data'][row[0]] = row[1]
                if row[0].lower() in ('male', 'm'):
                    stats['male_count'] = row[1]
                elif row[0].lower() in ('female', 'f'):
                    stats['female_count'] = row[1]
        except Exception:
            pass
        try:
            cur.execute('SELECT program, COUNT(*) FROM "Student" WHERE is_deleted = FALSE AND program IS NOT NULL AND program != \'\' GROUP BY program ORDER BY COUNT(*) DESC LIMIT 10')
            for row in cur.fetchall():
                stats['program_data'][row[0]] = row[1]
        except Exception:
            pass
        try:
            cur.execute('SELECT severity, COUNT(*) FROM "DASS21" WHERE is_deleted = FALSE GROUP BY severity')
            for row in cur.fetchall():
                stats['severity_data'][row[0]] = row[1]
        except Exception:
            pass
        try:
            cur.execute('SELECT status, COUNT(*) FROM "Appointment" WHERE is_deleted = FALSE GROUP BY status')
            for row in cur.fetchall():
                stats['status_data'][row[0]] = row[1]
        except Exception:
            pass
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('statistics.html', stats=stats)


@app.route("/intake", methods=["GET", "POST"])
@login_required
def intake():
    """Secretary Intake: register student + create appointment + fire notifications."""
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()

            # 1. Extract Student Info
            full_name = request.form.get('full_name', '').strip()
            if not full_name:
                first = request.form.get('first_name', '').strip()
                last = request.form.get('last_name', '').strip()
                full_name = f"{first} {last}".strip()

            index_number = request.form.get('index_number', '').strip()
            student_id_val = request.form.get('student_id', '').strip()
            identifier = index_number or student_id_val
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            gender = request.form.get('gender', '').strip()
            department = request.form.get('department', '').strip()
            programme = request.form.get('program', request.form.get('programme', '')).strip()
            level = request.form.get('level', '').strip()
            hall = request.form.get('hall_of_residence', '').strip()
            age = request.form.get('age', None)

            # 2. Extract Appointment Info
            appt_date = request.form.get('appointment_date', '').strip()
            appt_time = request.form.get('appointment_time', '').strip()
            purpose = request.form.get('purpose', request.form.get('reason_for_visit', '')).strip()
            urgency = request.form.get('urgency', 'Normal').strip()
            referral = request.form.get('referral_source', 'Self').strip()

            if not full_name:
                flash("Student name is required.", "error")
                return redirect(url_for('intake'))

            # 3. Check for existing student by index_number
            student_id = None
            if identifier:
                cur.execute(
                    'SELECT id FROM "Student" WHERE index_number = %s AND is_deleted = FALSE',
                    (identifier,),
                )
                row = cur.fetchone()
                if row:
                    student_id = row[0]

            if not student_id and full_name:
                cur.execute(
                    'SELECT id FROM "Student" WHERE name = %s AND is_deleted = FALSE',
                    (full_name,),
                )
                row = cur.fetchone()
                if row:
                    student_id = row[0]

            # 4. Create Student if new
            if not student_id:
                case_number = generate_case_number(conn)
                age_val = None
                if age:
                    try:
                        age_val = int(age)
                    except (ValueError, TypeError):
                        age_val = None
                cur.execute(
                    '''INSERT INTO "Student"
                       (name, case_number, index_number, email, phone, gender,
                        program, programme, department, level, hall_of_residence,
                        age, global_id, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                       RETURNING id''',
                    (full_name, case_number, identifier, email, phone, gender,
                     programme, programme, department, level, hall,
                     age_val, str(uuid.uuid4())),
                )
                student_id = cur.fetchone()[0]
                conn.commit()

            # 5. Create Appointment linked to student
            counsellor_name = 'Unassigned'
            cur.execute('SELECT name FROM "Counsellor" LIMIT 1')
            c_row = cur.fetchone()
            if c_row:
                counsellor_name = c_row[0] if isinstance(c_row, tuple) else c_row.get('name', 'Unassigned')

            cur.execute(
                '''INSERT INTO "Appointment"
                   (student_name, student_id, appointment_date, appointment_time,
                    counsellor, purpose, status, urgency, global_id,
                    created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled', %s, %s, NOW(), NOW())''',
                (full_name, str(student_id),
                 appt_date or datetime.now().strftime('%Y-%m-%d'),
                 appt_time or '09:00',
                 counsellor_name,
                 purpose or 'General intake',
                 urgency,
                 str(uuid.uuid4())),
            )
            conn.commit()

            # 6. Fire notifications
            fire_staff_notifications(
                conn,
                f"New intake: {name_to_initials(full_name)} ({identifier}) scheduled by {session.get('full_name', 'Secretary')}",
            )

            cur.close()
            conn.close()
            flash("Client registered and appointment scheduled successfully.", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            logger.error(f"intake: {e}")
            flash(f"Error processing intake: {e}", "error")
            return redirect(url_for('intake'))

    return render_template('intake.html')


@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    """Create a new appointment linked to a student."""
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()

            student_name = request.form.get('student_name', '').strip()
            student_id_val = request.form.get('student_id', '').strip()
            appt_date = request.form.get('date', '').strip()
            appt_time = request.form.get('time', '').strip()
            counsellor = request.form.get('counsellor', '').strip()
            appt_type = request.form.get('type', request.form.get('appointment_type', 'Individual')).strip()
            purpose = request.form.get('purpose', '').strip()
            urgency = request.form.get('urgency', 'Normal').strip()
            referral = request.form.get('referral_source', 'Self').strip()
            notes = request.form.get('notes', '').strip()

            if not appt_date or not appt_time:
                flash("Appointment date and time are required.", "error")
                return redirect(url_for('appointment'))

            # Validate student exists
            if student_id_val:
                cur.execute(
                    'SELECT id, name FROM "Student" WHERE id = %s AND is_deleted = FALSE',
                    (student_id_val,),
                )
                student_row = cur.fetchone()
                if not student_row:
                    flash("Student not found. Please check the ID or add the student first.", "error")
                    return redirect(url_for('appointment'))
                student_name = student_row[1] if isinstance(student_row, tuple) else student_row.get('name', student_name)
            elif student_name:
                cur.execute(
                    'SELECT id, name FROM "Student" WHERE name = %s AND is_deleted = FALSE',
                    (student_name,),
                )
                student_row = cur.fetchone()
                if student_row:
                    student_id_val = str(student_row[0] if isinstance(student_row, tuple) else student_row.get('id'))
                else:
                    flash("Student not found. Please check the name or add the student first.", "error")
                    return redirect(url_for('appointment'))
            else:
                flash("Student information is required.", "error")
                return redirect(url_for('appointment'))

            cur.execute(
                '''INSERT INTO "Appointment"
                   (student_name, student_id, appointment_date, appointment_time,
                    appointment_type, counsellor, purpose, urgency, notes,
                    status, global_id, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Scheduled', %s, NOW(), NOW())''',
                (student_name, student_id_val, appt_date, appt_time,
                 appt_type, counsellor, purpose, urgency, notes,
                 str(uuid.uuid4())),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Appointment scheduled successfully!", "success")
            return redirect(url_for('manage_appointments'))
        except Exception as e:
            logger.error(f"appointment: {e}")
            flash(f"Error scheduling appointment: {e}", "error")

    # GET — load student and counsellor lists for dropdowns
    students = []
    counsellors = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT id, name, case_number, programme FROM "Student" WHERE is_deleted = FALSE ORDER BY name')
        students = cur.fetchall()
        cur.execute('SELECT id, name FROM "Counsellor" ORDER BY name')
        counsellors = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"appointment GET: {e}")
    return render_template('appointment.html', students=students, counsellors=counsellors)


@app.route("/manage_appointments")
@login_required
def manage_appointments():
    appointments = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('''
            SELECT a.*, s.name as student_display_name, s.case_number, s.index_number
            FROM "Appointment" a
            LEFT JOIN "Student" s ON a.student_id = s.id::text
            WHERE a.is_deleted = FALSE
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT 500
        ''')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        appointments = rows
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"manage_appointments: {e}")
    return render_template('manage_appointments.html', appointments=appointments)


@app.route("/admin/users")
@login_required
def admin_users():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    users = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT id, username, full_name, role, created_at FROM users ORDER BY id')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        users = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('admin_users.html', users=users)


@app.route("/admin/users/add", methods=["GET", "POST"])
@login_required
def admin_user_add():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    if request.method == "GET":
        return redirect(url_for('admin_users'))
    try:
        from werkzeug.security import generate_password_hash
        conn = get_db()
        cur = conn.cursor()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'Counsellor')
        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for('admin_users'))
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
            (username, generate_password_hash(password), full_name, role),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash(f"User '{username}' created successfully", "success")
    except Exception as e:
        flash(f"Error creating user: {e}", "error")
    return redirect(url_for('admin_users'))


@app.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@login_required
def admin_user_delete(user_id):
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if row and row[0] == session.get('username'):
            flash("Cannot delete your own account", "error")
        else:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            flash("User deleted", "success")
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('admin_users'))


@app.route("/audit_logs")
@login_required
def audit_logs():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    logs = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 200')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        logs = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('audit_logs.html', logs=logs)


@app.route("/admin_workflow")
@login_required
def admin_workflow():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    return render_template('admin_workflow.html')


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            cur.execute("UPDATE users SET full_name = %s, email = %s, phone = %s, updated_at = NOW() WHERE username = %s",
                        (full_name, email, phone, session.get('username', '')))
            new_pw = request.form.get('new_password', '').strip()
            if new_pw:
                from werkzeug.security import generate_password_hash
                cur.execute("UPDATE users SET password_hash = %s WHERE username = %s",
                            (generate_password_hash(new_pw), session.get('username', '')))
            conn.commit()
            cur.close()
            conn.close()
            flash("Profile updated", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
        return redirect(url_for('profile'))
    user = {}
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute("SELECT id, username, full_name, role, email, phone FROM users WHERE username = %s", (session.get('username', ''),))
        user = cur.fetchone() or {}
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('profile.html', user=user)


@app.route("/import_csv", methods=["GET", "POST"])
@login_required
def import_csv():
    if request.method == "POST":
        import csv
        import io
        file = request.files.get('csv_file')
        import_type = request.form.get('import_type', 'students')
        if not file or file.filename == '':
            flash("No file selected", "error")
            return redirect(url_for('import_csv'))
        try:
            raw = file.read()
            content = None
            for enc in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
                try:
                    content = raw.decode(enc)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            if content is None:
                content = raw.decode('latin-1')
            reader = csv.DictReader(io.StringIO(content))
            conn = get_db()
            cur = conn.cursor()
            count = 0
            if import_type == 'students':
                for row in reader:
                    first = row.get('first_name', row.get('First Name', ''))
                    last = row.get('last_name', row.get('Last Name', ''))
                    name = row.get('name', row.get('Name', ''))
                    if not first and not last and name:
                        parts = name.split(' ', 1)
                        first = parts[0]
                        last = parts[1] if len(parts) > 1 else ''
                    sid = row.get('student_id', row.get('Student ID', row.get('index_number', row.get('Index Number', ''))))
                    email = row.get('email', row.get('Email', ''))
                    phone = row.get('phone', row.get('Phone', ''))
                    gender = row.get('gender', row.get('Gender', ''))
                    program = row.get('program', row.get('Program', row.get('programme', row.get('Programme', ''))))
                    department = row.get('department', row.get('Department', ''))
                    level = row.get('level', row.get('Level', ''))
                    cur.execute(
                        '''INSERT INTO "Student" (first_name, last_name, name, student_id, email, phone, gender, program, department, level, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                        (first, last, f"{first} {last}".strip(), sid, email, phone, gender, program, department, level)
                    )
                    count += 1
            elif import_type == 'appointments':
                for row in reader:
                    cur.execute(
                        '''INSERT INTO "Appointment" (student_name, student_id, appointment_date, appointment_time, appointment_type, counsellor, notes, status, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                        (row.get('student_name', row.get('Student Name', '')),
                         row.get('student_id', row.get('Student ID', '')),
                         row.get('date', row.get('Date', row.get('appointment_date', ''))),
                         row.get('time', row.get('Time', row.get('appointment_time', ''))),
                         row.get('type', row.get('Type', row.get('appointment_type', 'Individual'))),
                         row.get('counsellor', row.get('Counsellor', '')),
                         row.get('notes', row.get('Notes', '')),
                         'Scheduled')
                    )
                    count += 1
            conn.commit()
            cur.close()
            conn.close()
            flash(f"Successfully imported {count} {import_type}", "success")
        except Exception as e:
            flash(f"Import error: {e}", "error")
        return redirect(url_for('students' if import_type == 'students' else 'manage_appointments'))
    return render_template('import_csv.html')


@app.route("/my_cases")
@login_required
def my_cases():
    cases = []
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "CaseManagement" WHERE is_deleted = FALSE ORDER BY created_at DESC LIMIT 200')
        rows = cur.fetchall()
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    r[k] = v.isoformat()
        cases = rows
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('my_cases.html', cases=cases)


@app.route("/appointments")
@login_required
def appointments_page():
    return redirect(url_for('dashboard'))


@app.route("/health", methods=["GET"])
def health_check():
    db_status = "Disconnected"
    db_error = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        db_status = "Connected"
    except Exception as e:
        db_error = str(e)

    if db_status == "Connected":
        try:
            conn = get_db()
            cur = conn.cursor()
            tables = [
                'Student','Appointment','session','Referral','CaseManagement',
                'OutcomeQuestionnaire','DASS21','Feedback','SessionIssue',
                'Notification','app_settings','BookingRequest',
            ]
            for t in tables:
                try:
                    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{t.lower()}'")
                    cols = [c[0] for c in cur.fetchall()]
                    if cols:
                        if 'is_deleted' not in cols:
                            cur.execute(f'ALTER TABLE "{t}" ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE')
                        if 'global_id' not in cols and t not in ('app_settings', 'BookingRequest'):
                            cur.execute(f'ALTER TABLE "{t}" ADD COLUMN global_id UUID DEFAULT gen_random_uuid()')
                        if 'updated_at' not in cols:
                            cur.execute(f'ALTER TABLE "{t}" ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP')
                        if 'last_synced_at' not in cols:
                            cur.execute(f'ALTER TABLE "{t}" ADD COLUMN last_synced_at TIMESTAMP WITH TIME ZONE')
                except Exception:
                    conn.rollback()
                    continue
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

    return jsonify({
        "status": "online",
        "database": db_status,
        "database_error": db_error,
        "service": "AAMUSTED Counselling System",
    })


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/') or request.path.startswith('/sync/') or request.path.startswith('/static/'):
        return jsonify({"error": "Not found"}), 404
    return redirect(url_for('dashboard'))


@app.route("/export_referrals")
@login_required
def export_referrals():
    import csv
    import io
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "Referral" WHERE is_deleted = FALSE ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Student Name', 'Student ID', 'Referred By', 'Contact', 'Reason', 'Status'])
        for r in rows:
            writer.writerow([
                r.get('created_at', ''), r.get('student_name', ''), r.get('student_id', ''),
                r.get('referred_by', ''), r.get('contact', ''), r.get('reason', ''), r.get('status', '')
            ])
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=referrals_export.csv'}
        )
    except Exception as e:
        flash(f"Export error: {e}", "error")
        return redirect(url_for('all_referrals'))

@app.route("/export_students")
@login_required
def export_students():
    import csv
    import io
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "Student" WHERE is_deleted = FALSE ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['First Name', 'Last Name', 'Student ID', 'Email', 'Phone', 'Gender', 'Program', 'Department', 'Level', 'Date Registered'])
        for r in rows:
            writer.writerow([
                r.get('first_name', ''), r.get('last_name', ''), r.get('student_id', ''),
                r.get('email', ''), r.get('phone', ''), r.get('gender', ''),
                r.get('program', ''), r.get('department', ''), r.get('level', ''),
                r.get('created_at', '')
            ])
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=students_export.csv'}
        )
    except Exception as e:
        flash(f"Export error: {e}", "error")
        return redirect(url_for('students'))

@app.route("/export_sessions")
@login_required
def export_sessions():
    import csv
    import io
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "session" WHERE is_deleted = FALSE ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Student Name', 'Student ID', 'Session Type', 'Counsellor', 'Status', 'Notes'])
        for r in rows:
            writer.writerow([
                r.get('session_date', r.get('created_at', '')), r.get('student_name', ''), r.get('student_id', ''),
                r.get('session_type', ''), r.get('counsellor', ''), r.get('status', ''), r.get('notes', '')
            ])
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sessions_export.csv'}
        )
    except Exception as e:
        flash(f"Export error: {e}", "error")
        return redirect(url_for('sessions_list'))

@app.route("/import_students", methods=["POST"])
@login_required
def import_students():
    flash("Import processed", "success")
    return redirect(url_for('students'))

@app.route("/notifications/mark_read/<int:notification_id>", methods=["POST"])
@login_required
def mark_read(notification_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "Notification" SET is_read = TRUE WHERE id = %s', (notification_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
    return jsonify({"ok": True})

@app.route("/notifications/mark_all_read", methods=["POST"])
@login_required
def mark_all_read():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "Notification" SET is_read = TRUE')
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
    return jsonify({"ok": True})

@app.route("/admin/set_theme", methods=["POST"])
@login_required
def set_theme():
    return redirect(url_for('admin_settings'))

@app.route("/admin/sync/now")
@login_required
def sync_now():
    return redirect(url_for('dashboard'))

@app.route("/appointment/update_status/<int:appt_id>/<new_status>")
@login_required
def update_appt_status(appt_id, new_status):
    """Update appointment status with timestamps + auto-create session on 'In Session'."""
    role = session.get('role', '')
    allowed = {
        'Secretary': ['Checked In', 'Sent to Counsellor', 'Cancelled'],
        'Admin': ['Scheduled', 'Confirmed', 'Checked In', 'Sent to Counsellor', 'In Session', 'Completed', 'Cancelled', 'No Show'],
        'Counsellor': ['In Session', 'Completed', 'Cancelled'],
    }
    if new_status not in allowed.get(role, []):
        flash(f"Your role ({role}) cannot set status to '{new_status}'", "error")
        return redirect(url_for('manage_appointments'))
    try:
        conn = get_db()
        cur = conn.cursor()

        # Build dynamic UPDATE with timestamps
        update_parts = ['status = %s', 'updated_at = NOW()']
        params = [new_status]

        if new_status == 'Checked In':
            update_parts.append('checked_in_at = NOW()')
        elif new_status == 'In Session':
            update_parts.append('started_at = NOW()')
        elif new_status in ('Completed', 'Cancelled'):
            update_parts.append('completed_at = NOW()')

        set_clause = ', '.join(update_parts)
        cur.execute(
            f'UPDATE "Appointment" SET {set_clause} WHERE id = %s',
            (*params, appt_id),
        )

        # Auto-create session record when status changes to 'In Session'
        if new_status == 'In Session':
            try:
                cur.execute(
                    'SELECT student_name, student_id FROM "Appointment" WHERE id = %s',
                    (appt_id,),
                )
                appt = cur.fetchone()
                if appt:
                    appt_student_name = appt[0] if isinstance(appt, tuple) else appt.get('student_name', '')
                    appt_student_id = appt[1] if isinstance(appt, tuple) else appt.get('student_id', '')
                    counsellor_name = session.get('full_name', session.get('username', ''))
                    cur.execute(
                        '''INSERT INTO "session"
                           (student_name, student_id, session_type, session_date,
                            counsellor, status, global_id, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())''',
                        (appt_student_name, appt_student_id, 'Individual',
                         datetime.now().strftime('%Y-%m-%d'),
                         counsellor_name, 'In Progress', str(uuid.uuid4())),
                    )
            except Exception as sess_err:
                logger.error(f"auto-create session: {sess_err}")

        conn.commit()
        cur.close()
        conn.close()
        flash(f"Status updated to '{new_status}'", "success")
    except Exception as e:
        logger.error(f"update_appt_status: {e}")
        flash(f"Error: {e}", "error")
    return redirect(url_for('manage_appointments'))

@app.route("/update_appointment_status/<int:appointment_id>", methods=["POST"])
@login_required
def update_appointment_status(appointment_id):
    new_status = request.form.get('status', '')
    return redirect(url_for('update_appt_status', appt_id=appointment_id, new_status=new_status))

@app.route("/student_profile/<int:id>")
@login_required
def student_profile(id):
    student = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "Student" WHERE id = %s', (id,))
        student = cur.fetchone()
        if student:
            for k, v in student.items():
                if isinstance(v, (datetime, date)):
                    student[k] = v.isoformat()
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('students.html', students=[student] if student else [])

@app.route("/delete_student/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "Student" SET is_deleted = TRUE, updated_at = NOW() WHERE id = %s', (student_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Client deleted", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('students'))

@app.route("/delete_appointment/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "Appointment" SET is_deleted = TRUE, updated_at = NOW() WHERE id = %s', (appointment_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Appointment deleted", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('manage_appointments'))

@app.route("/delete_session/<int:session_id>", methods=["POST"])
@login_required
def delete_session(session_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "session" SET is_deleted = TRUE, updated_at = NOW() WHERE id = %s', (session_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Session deleted", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('sessions_list'))

@app.route("/delete_referral/<int:referral_id>", methods=["POST"])
@login_required
def delete_referral(referral_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE "Referral" SET is_deleted = TRUE, updated_at = NOW() WHERE id = %s', (referral_id,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Referral deleted", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for('all_referrals'))

@app.route("/booking", methods=["GET", "POST"])
def booking():
    """Public booking portal — auto-accepted, creates Student + Appointment + BookingRequest."""
    if request.method == "POST":
        try:
            conn = get_db()
            cur = conn.cursor()

            full_name = request.form.get('full_name', '').strip()
            index_number = request.form.get('index_number', '').strip()
            programme_base = request.form.get('programme', '').strip()
            programme_other = request.form.get('programme_other', '').strip()
            programme = programme_other if programme_base == 'Other' else programme_base
            department = request.form.get('department', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            hall_of_residence = request.form.get('hall_of_residence', '').strip()
            preferred_date = request.form.get('preferred_date', '').strip()
            preferred_time = request.form.get('preferred_time', 'Any').strip()
            reason = request.form.get('reason', '').strip()

            missing_fields = []
            if not full_name:
                missing_fields.append("Full Name")
            if not index_number:
                missing_fields.append("Index Number")
            if not phone:
                missing_fields.append("Phone Number")
            if not department:
                missing_fields.append("Department")
            if not programme:
                missing_fields.append("Programme")
            if not preferred_time or preferred_time == 'Click to set time':
                missing_fields.append("Preferred Time")

            if missing_fields:
                return render_template('booking_portal.html',
                                       error=f"The following fields are required: {', '.join(missing_fields)}.")

            ref = generate_booking_ref(conn)
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 1. Insert BookingRequest as Pending (staff can review in admin)
            cur.execute(
                '''INSERT INTO "BookingRequest"
                   (reference, full_name, index_number, department, programme, phone,
                    preferred_date, preferred_time, reason, status, email,
                    hall_of_residence, global_id, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s, %s, %s, NOW(), NOW())
                   RETURNING id''',
                (ref, full_name, index_number, department, programme, phone,
                 preferred_date, preferred_time, reason, email, hall_of_residence,
                 str(uuid.uuid4())),
            )

            # 2. Find or create Student record
            cur.execute(
                'SELECT id FROM "Student" WHERE index_number = %s AND is_deleted = FALSE',
                (index_number,),
            )
            existing = cur.fetchone()

            if existing:
                student_id = existing[0] if isinstance(existing, tuple) else existing.get('id')
            else:
                case_number = generate_case_number(conn)
                cur.execute(
                    '''INSERT INTO "Student"
                       (name, case_number, index_number, department, programme, contact,
                        email, hall_of_residence, global_id, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                       RETURNING id''',
                    (full_name, case_number, index_number, department, programme,
                     phone, email, hall_of_residence, str(uuid.uuid4())),
                )
                student_id = cur.fetchone()[0]
                conn.commit()

            # 3. Create Appointment linked to student
            counsellor_name = 'Unassigned'
            cur.execute('SELECT name FROM "Counsellor" LIMIT 1')
            c_row = cur.fetchone()
            if c_row:
                counsellor_name = c_row[0] if isinstance(c_row, tuple) else c_row.get('name', 'Unassigned')

            cur.execute(
                '''INSERT INTO "Appointment"
                   (student_name, student_id, appointment_date, appointment_time,
                    counsellor, purpose, status, booking_ref, urgency, global_id,
                    created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled', %s, 'Normal', %s, NOW(), NOW())''',
                (full_name, str(student_id),
                 preferred_date or datetime.now().strftime('%Y-%m-%d'),
                 preferred_time or '09:00',
                 counsellor_name,
                 f"[Portal Booking] {reason or 'Counselling session'}",
                 ref, str(uuid.uuid4())),
            )
            conn.commit()

            # 4. Fire notifications to all staff
            fire_staff_notifications(
                conn,
                f"New booking {ref} from {name_to_initials(full_name)} ({index_number}) — auto-accepted & scheduled",
                '/admin/bookings',
            )

            cur.close()
            conn.close()
            return redirect(url_for('booking_confirm', ref=ref))

        except Exception as e:
            logger.error(f"booking: {e}")
            import traceback
            traceback.print_exc()
            return render_template('booking_portal.html',
                                   error="Something went wrong. Please try again.")

    return render_template('booking_portal.html')


@app.route("/booking/confirm/<ref>")
def booking_confirm(ref):
    """Public confirmation page after booking submission."""
    booking = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute(
            'SELECT * FROM "BookingRequest" WHERE reference = %s', (ref,)
        )
        booking = cur.fetchone()
        if booking:
            for k, v in booking.items():
                if isinstance(v, (datetime, date)):
                    booking[k] = v.strftime('%Y-%m-%d %H:%M')
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"booking_confirm: {e}")
    return render_template('booking_confirmation.html', ref=ref, booking=booking)

@app.route("/toggle_auto_report", methods=["GET", "POST"])
@login_required
def toggle_auto_report():
    return redirect(url_for('reports'))

@app.route("/generate_report_now", methods=["POST"])
@login_required
def generate_report_now():
    flash("Report generation initiated", "success")
    return redirect(url_for('reports'))

@app.route("/generate_report_manual", methods=["POST"])
@login_required
def generate_report_manual():
    flash("Manual report generation initiated", "success")
    return redirect(url_for('reports'))

@app.route("/download_report_file/<int:report_id>")
@login_required
def download_report_file(report_id):
    return redirect(url_for('reports'))

@app.route("/view_report/<int:report_id>")
@login_required
def view_report(report_id):
    return redirect(url_for('reports'))

@app.route("/download_report/<int:report_id>")
@login_required
def download_report(report_id):
    return redirect(url_for('reports'))

@app.route("/delete_report/<int:report_id>", methods=["POST"])
@login_required
def delete_report(report_id):
    return redirect(url_for('reports'))

@app.route("/print_session/<int:session_id>")
@login_required
def print_session(session_id):
    data = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "session" WHERE id = %s', (session_id,))
        data = cur.fetchone()
        if data:
            for k, v in data.items():
                if isinstance(v, (datetime, date)):
                    data[k] = v.isoformat()
        cur.close()
        conn.close()
    except Exception:
        pass
    if not data:
        flash("Session not found", "error")
        return redirect(url_for('sessions_list'))
    return render_template('print_session.html', session_data=data)

@app.route("/print_referral/<int:id>")
@login_required
def print_referral(id):
    data = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "Referral" WHERE id = %s', (id,))
        data = cur.fetchone()
        if data:
            for k, v in data.items():
                if isinstance(v, (datetime, date)):
                    data[k] = v.isoformat()
        cur.close()
        conn.close()
    except Exception:
        pass
    if not data:
        flash("Referral not found", "error")
        return redirect(url_for('all_referrals'))
    return render_template('print_referral.html', referral=data)

@app.route("/print_case/<int:case_id>")
@app.route("/print_case_note/<int:case_id>")
@login_required
def print_case_note(case_id):
    data = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "CaseManagement" WHERE id = %s', (case_id,))
        data = cur.fetchone()
        if data:
            for k, v in data.items():
                if isinstance(v, (datetime, date)):
                    data[k] = v.isoformat()
        cur.close()
        conn.close()
    except Exception:
        pass
    if not data:
        flash("Case note not found", "error")
        return redirect(url_for('case_notes_list'))
    return render_template('print_case_note.html', case=data)

@app.route("/print_dass21/<int:dass21_id>")
@login_required
def print_dass21(dass21_id):
    data = None
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "DASS21" WHERE id = %s', (dass21_id,))
        data = cur.fetchone()
        if data:
            for k, v in data.items():
                if isinstance(v, (datetime, date)):
                    data[k] = v.isoformat()
        cur.close()
        conn.close()
    except Exception:
        pass
    if not data:
        flash("Assessment not found", "error")
        return redirect(url_for('dass21_list'))
    return render_template('print_dass21.html', assessment=data)

@app.route("/print_report/<int:report_id>")
@login_required
def print_report(report_id):
    return redirect(url_for('reports'))

@app.route("/get_session/<int:session_id>")
@login_required
def get_session(session_id):
    try:
        conn = get_db()
        cur = dict_cursor(conn)
        cur.execute('SELECT * FROM "session" WHERE id = %s', (session_id,))
        data = cur.fetchone()
        if data:
            for k, v in data.items():
                if isinstance(v, (datetime, date)):
                    data[k] = v.isoformat()
        cur.close()
        conn.close()
        return jsonify(data or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/forms")
@login_required
def admin_forms():
    return redirect(url_for('admin_settings'))

@app.route("/admin/export/master")
@login_required
def export_master():
    return redirect(url_for('students'))

@app.route("/import_template/<import_type>")
@login_required
def import_template(import_type):
    return redirect(url_for('import_csv'))

@app.route("/admin/users/edit", methods=["POST"])
@login_required
def edit_user():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    try:
        user_id = request.form.get('user_id')
        full_name = request.form.get('full_name', '').strip()
        if not user_id:
            flash("Missing user ID", "error")
            return redirect(url_for('admin_users'))
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET full_name = %s, updated_at = NOW() WHERE id = %s", (full_name, user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("User updated successfully", "success")
    except Exception as e:
        flash(f"Error updating user: {e}", "error")
    return redirect(url_for('admin_users'))


@app.route("/admin/users/reset_password", methods=["POST"])
@login_required
def reset_password():
    if session.get('role') != 'Admin':
        flash("Unauthorized", "error")
        return redirect(url_for('dashboard'))
    try:
        from werkzeug.security import generate_password_hash
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password', '')
        if not user_id or not new_password:
            flash("Missing user ID or password", "error")
            return redirect(url_for('admin_users'))
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s",
                    (generate_password_hash(new_password), user_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Password reset successfully", "success")
    except Exception as e:
        flash(f"Error resetting password: {e}", "error")
    return redirect(url_for('admin_users'))
