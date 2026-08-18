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
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
            ('admin', generate_password_hash('admin123'), 'System Admin', 'Admin')
        )
    cur.execute("SELECT id FROM users WHERE username = 'secretary'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
            ('secretary', generate_password_hash('secretary123'), 'Desk Secretary', 'Secretary')
        )
    cur.execute("SELECT id FROM users WHERE username = 'counsellor'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
            ('counsellor', generate_password_hash('counsellor123'), 'Default Counsellor', 'Counsellor')
        )
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "Counsellor" (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT,
            specialization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute('SELECT id FROM "Counsellor" WHERE name = %s', ('Default Counsellor',))
    if not cur.fetchone():
        cur.execute('INSERT INTO "Counsellor" (name, contact) VALUES (%s, %s)', ('Default Counsellor', ''))
    conn.commit()
    cur.close()
    conn.close()


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
    stats = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM \"Student\" WHERE is_deleted = FALSE")
        stats['total_students'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM \"Appointment\" WHERE is_deleted = FALSE")
        stats['total_appointments'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM \"BookingRequest\" WHERE status = 'Pending'")
        stats['pending_bookings'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM \"session\" WHERE is_deleted = FALSE")
        stats['total_sessions'] = cur.fetchone()[0]
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"dashboard: {e}")
    return render_template('dashboard.html', stats=stats)


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
