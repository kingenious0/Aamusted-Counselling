import os
import logging
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "sb_bridge_AnEpYo_2026")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is missing in Vercel settings")
    if 'sslmode=' in DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def verify_api_key():
    key = request.headers.get("X-API-KEY")
    return key == BRIDGE_API_KEY

@app.route("/", methods=["GET"])
def health_check():
    db_status = "Disconnected"
    db_error = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        db_status = "Connected"
    except Exception as e:
        db_error = str(e)
        logger.error(f"Database connection error: {e}")

    # Dynamic Migration (safely non-blocking)
    if db_status == "Connected":
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            tables = ['Student', 'Appointment', 'session', 'Referral', 'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 'Feedback', 'SessionIssue', 'Notification', 'app_settings', 'BookingRequest']
            for table in tables:
                try:
                    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table.lower()}'")
                    cols = [c[0] for c in cur.fetchall()]
                    if cols:
                        if 'is_deleted' not in cols:
                            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE')
                        if 'global_id' not in cols and table not in ['app_settings', 'BookingRequest']:
                            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN global_id UUID DEFAULT gen_random_uuid()')
                        if 'updated_at' not in cols:
                            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP')
                        if 'last_synced_at' not in cols:
                            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN last_synced_at TIMESTAMP WITH TIME ZONE')
                except Exception as table_err:
                    logger.warning(f"Skipping table {table} during migration: {table_err}")
                    conn.rollback()
                    continue
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Migration warning: {e}")

    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        color = "#28a745" if db_status == "Connected" else "#dc3545"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AAMUSTED Counselling - Cloud Sync Bridge</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }}
                .card {{ background: #1e293b; padding: 32px; border-radius: 16px; border: 1px solid #334155; max-width: 540px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
                .badge {{ display: inline-block; padding: 6px 14px; border-radius: 20px; font-weight: bold; background: {color}; color: #fff; font-size: 14px; }}
                h1 {{ margin: 0 0 12px 0; font-size: 24px; color: #f8fafc; }}
                p {{ color: #94a3b8; line-height: 1.5; font-size: 14px; }}
                .stat-box {{ background: #0f172a; padding: 14px; border-radius: 8px; margin: 16px 0; border: 1px solid #334155; font-family: monospace; font-size: 13px; color: #38bdf8; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🏛️ AAMUSTED GCC Cloud Bridge</h1>
                <p>This is the serverless cloud synchronization engine connecting the desktop Progressive Web App to Supabase PostgreSQL.</p>
                <div style="margin: 20px 0;">
                    <span class="badge">● Cloud Bridge: Online</span>
                    <span class="badge" style="margin-left: 8px;">● Supabase DB: {db_status}</span>
                </div>
                <div class="stat-box">
                    Sync Endpoint: /sync/pull & /sync/push<br>
                    Booking Endpoint: /api/submit_booking<br>
                    {f"DB Error: {db_error}" if db_error else "Database: Connected & Ready"}
                </div>
                <p style="font-size: 12px; color: #64748b;">The full clinical management system runs locally as an offline-first desktop PWA on staff computers and syncs bidirectionally through this bridge.</p>
            </div>
        </body>
        </html>
        """

    return jsonify({
        "status": "online",
        "database": db_status,
        "database_error": db_error,
        "environment": "Vercel",
        "service": "AAMUSTED Counselling Cloud Bridge"
    })

@app.route("/sync/stats", methods=["GET"])
def sync_stats():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        tables = [
            'Student', 'Appointment', 'session', 'Referral', 
            'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
            'Feedback', 'SessionIssue', 'Notification', 'app_settings',
            'BookingRequest'
        ]
        
        counts = {}
        for table in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                counts[table] = cur.fetchone()[0]
            except Exception as e:
                logger.error(f"Error counting table {table}: {e}")
                cur.execute("ROLLBACK")
                counts[table] = -1
        
        cur.close()
        conn.close()
        return jsonify({"status": "success", "counts": counts})
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/sync/push", methods=["POST"])
def push_changes():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json or {}
    changes = data.get("changes", {})
    records = data.get("records")
    table_name = data.get("table")
    cleanup_tables = data.get("cleanup_tables", [])
    
    if table_name and records:
        changes = {table_name: records}
        
    if not isinstance(changes, dict):
        return jsonify({"error": "Invalid format"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        for table in cleanup_tables:
            cur.execute(f'DELETE FROM "{table}"')
            logger.info(f"Purged table {table}")

        stats = {}
        for table, record_list in changes.items():
            stats[table] = 0
            for record in record_list:
                try:
                    clean_record = {k: v for k, v in record.items() if k != 'id'}
                    
                    for k in ['is_deleted', 'is_read']:
                        if k in clean_record:
                            clean_record[k] = bool(clean_record[k])
                    
                    cols = list(clean_record.keys())
                    vals = [clean_record[c] for c in cols]
                    
                    if table == "app_settings":
                        conflict_target = "setting_name"
                    elif table == "BookingRequest":
                        conflict_target = "reference"
                    else:
                        conflict_target = "global_id"
                    
                    # LWW: Only overwrite if incoming record is newer
                    incoming_ts = clean_record.get('updated_at', '1970-01-01 00:00:00')
                    cur.execute(
                        f'SELECT updated_at FROM "{table}" WHERE "{conflict_target}" = %s',
                        (clean_record.get(conflict_target),)
                    )
                    existing = cur.fetchone()
                    if existing and existing[0] and incoming_ts and incoming_ts <= str(existing[0]):
                        stats[table] += 1  # Count as handled but skipped
                        continue  # Local is newer or same — skip
                    
                    placeholders = ", ".join(["%s"] * len(cols))
                    update_stmt = ", ".join([f'"{c}" = EXCLUDED."{c}"' for c in cols if c != conflict_target])
                    
                    query = f"""
                        INSERT INTO "{table}" ({', '.join([f'"{c}"' for c in cols])})
                        VALUES ({placeholders})
                        ON CONFLICT ("{conflict_target}") DO UPDATE SET {update_stmt}
                    """
                    cur.execute(query, tuple(vals))
                    stats[table] += 1
                except Exception as rec_err:
                    logger.error(f"Error in {table}: {rec_err}")
                    conn.rollback()
                    continue
            
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "counts": stats}), 200
        
    except Exception as e:
        logger.error(f"Push error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/sync/pull", methods=["POST"])
def pull_data():
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json or {}
    since = data.get("last_sync_timestamp")
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        tables = [
            'Student', 'Appointment', 'session', 'Referral', 
            'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
            'Feedback', 'SessionIssue', 'Notification', 'app_settings',
            'BookingRequest'
        ]
        
        all_changes = {}
        total_count = 0
        
        for table in tables:
            query = f'SELECT * FROM "{table}"'
            if since and since != '1970-01-01 00:00:00':
                query += " WHERE updated_at > %s"
                cur.execute(query, (since,))
            else:
                cur.execute(query)
                
            records = cur.fetchall()
            if records:
                sanitized_records = []
                for r in records:
                    r_dict = dict(r)
                    if not r_dict.get('global_id') and table not in ['app_settings', 'BookingRequest']:
                        r_dict['global_id'] = f"cloud-{table}-{r_dict.get('id')}"
                    sanitized_records.append(r_dict)
                
                all_changes[table] = sanitized_records
                total_count += len(sanitized_records)
                
        cur.close()
        conn.close()
        
        for table in all_changes:
            for record in all_changes[table]:
                for k, v in record.items():
                    if isinstance(v, datetime):
                        record[k] = v.strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "changes": all_changes,
            "count": total_count,
            "server_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        logger.error(f"Pull error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/submit_booking", methods=["POST"])
def portal_booking():
    data = request.json or {}
    try:
        if not data.get('reference'):
            import random
            import string
            data['reference'] = 'BR-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        if not data.get('global_id'):
            data['global_id'] = str(uuid.uuid4())
        
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = now
        data['created_at'] = now
        if not data.get('status'):
            data['status'] = 'Pending'

        conn = get_db_connection()
        cur = conn.cursor()
        
        KNOWN_COLUMNS = [
            'reference', 'full_name', 'index_number', 'department', 
            'programme', 'phone', 'preferred_date', 'preferred_time', 
            'reason', 'status', 'email', 'hall_of_residence',
            'gender', 'age',
            'global_id', 'updated_at', 'created_at'
        ]
        
        columns = [c for c in data.keys() if c in KNOWN_COLUMNS]
        values = [data[column] for column in columns]
        placeholders = ", ".join(["%s"] * len(columns))
        
        query = f'INSERT INTO "BookingRequest" ({", ".join([f\'"{c}"\' for c in columns])}) VALUES ({placeholders}) RETURNING reference'
        cur.execute(query, values)
        ref = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "reference": ref}), 201
        
    except Exception as e:
        logger.error(f"Portal error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

