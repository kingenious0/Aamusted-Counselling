import sqlite3
import json
import requests
import threading
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import node_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyncEngine")

# Create Blueprint
sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

# Tables to sync (Properly Cased for Cloud Bridge matching)
SYNC_TABLES = [
    'Student', 'Appointment', 'session', 'Referral', 
    'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
    'Feedback', 'SessionIssue', 'Notification', 'app_settings',
    'BookingRequest'
]

def get_db_connection():
    """Helper to get DB connection from the main app's logic."""
    import app
    return app.get_db_connection()

# ==========================================
# CLIENT LOGIC (Automated Background Sync)
# ==========================================

class AutomatedSyncManager:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.thread.start()
            logger.info("Background Automated Sync started.")

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)

    def _sync_loop(self):
        """Main loop for background synchronization."""
        while not self.stop_event.is_set():
            try:
                self.run_automated_sync()
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
            
            # Wait for next cycle (default 10 seconds for real-time responsiveness)
            config = node_config.load_config()
            interval = config.get('sync_interval_seconds', 10)
            self.stop_event.wait(interval)

    def run_automated_sync(self):
        """Checks for local changes and pushes them, and pulls remote changes."""
        config = node_config.load_config()
        if not config.get('sync_enabled', True):
            return

        cloud_url = config.get('cloud_api_url')
        api_key = config.get('cloud_api_key')
        if not cloud_url:
            return

        # 1. PUSH local changes to Cloud
        self.push_pending_changes(cloud_url, api_key)

        # 2. PULL remote changes from Cloud
        self.pull_remote_changes(cloud_url, api_key)

        # 3. LOCAL P2P Fallback (Sync with Peer if on same Wi-Fi)
        peer_ip = config.get('peer_ip')
        if peer_ip:
            self.p2p_network_sync(peer_ip, api_key)

    def p2p_network_sync(self, peer_ip, api_key):
        """Attempts to sync directly with a peer on the same local network."""
        peer_url = f"http://{peer_ip}:5050/api/sync"
        try:
            # Simple health check to see if peer is reachable
            # (Just try to push a small batch or check status)
            logger.info(f"Attempting Local P2P Sync with {peer_ip}...")
            
            # Re-use push logic but directed at peer
            # We don't mark as 'synced' with cloud because the cloud still needs it,
            # but we update the peer's database.
            self._push_to_target(peer_url, api_key, mark_as_synced=False)
            
            # Pull from peer (mimic cloud pull)
            self._pull_from_target(peer_url, api_key)
            
        except Exception as e:
            logger.debug(f"P2P sync skipped (Peer unreachable): {e}")

    def push_pending_changes(self, cloud_url, api_key):
        """Finds all records changed locally and pushes them to cloud with batching."""
        self._push_to_target(cloud_url, api_key, mark_as_synced=True)

    def _push_to_target(self, target_url, api_key, mark_as_synced=True):
        """Generic push logic for any target (Cloud or Peer)."""
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            for table in SYNC_TABLES:
                # Find records that need syncing
                query = f"SELECT * FROM {table} WHERE last_synced_at IS NULL OR updated_at > last_synced_at"
                pending = cursor.execute(query).fetchall()
                
                if not pending:
                    continue

                logger.info(f"Syncing {len(pending)} records for table {table} in batches...")
                
                # Push in batches of 30 to prevent network timeouts
                batch_size = 30
                for i in range(0, len(pending), batch_size):
                    batch_rows = pending[i : i + batch_size]
                    records = [dict(r) for r in batch_rows]
                    
                    try:
                        resp = requests.post(
                            f"{target_url}/push", 
                            json={
                                "table": table, 
                                "records": records, 
                                "api_key": api_key, 
                                "node_id": node_config.get_node_id()
                            },
                            headers={"X-API-KEY": api_key},
                            timeout=30 # Increased timeout for large batches
                        )
                        
                        if resp.status_code == 200:
                            # Mark as synced locally
                            sync_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                            for record in batch_rows:
                                # Ensure we have a global_id before updating local marker
                                if record.get('global_id'):
                                    cursor.execute(
                                        f"UPDATE {table} SET last_synced_at = ? WHERE global_id = ?",
                                        (sync_timestamp, record['global_id'])
                                    )
                            conn.commit()
                            logger.info(f"Successfully pushed batch {i//batch_size + 1} for {table}. Bridge said: {resp.text[:100]}")
                        else:
                            logger.warning(f"Failed to push batch for {table}: Code {resp.status_code} - {resp.text[:200]}")
                    except Exception as e:
                        logger.error(f"Network error pushing batch for {table}: {e}")
                        break # Stop further batches for this table on error
                    
        finally:
            conn.close()

    def pull_remote_changes(self, cloud_url, api_key):
        """Pulls changes from cloud to local (e.g. new BookingRequests)."""
        self._pull_from_target(cloud_url, api_key)

    def _pull_from_target(self, target_url, api_key):
        """Generic pull logic for any target (Cloud or Peer)."""
        config = node_config.load_config()
        last_pull_ts = config.get('last_cloud_sync', '1970-01-01 00:00:00')
        
        try:
            resp = requests.post(
                f"{target_url}/pull", 
                json={
                    "last_sync_timestamp": last_pull_ts, 
                    "api_key": api_key, 
                    "node_id": node_config.get_node_id()
                },
                headers={"X-API-KEY": api_key},
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                changes = data.get('changes', {})
                count = data.get('count', 0)
                server_time = data.get('server_time')
                
                new_bookings_count = 0
                if count > 0:
                    # Capture counts before applying
                    p_rows = apply_incoming_changes(changes)
                    logger.info(f"Pulled {count} changes from cloud. Applied {p_rows} rows.")
                    
                    # Logic: Only alert if we actually applied NEW BookingRequests created RECENTLY
                    if 'BookingRequest' in changes:
                        has_real_new = False
                        try:
                            now = datetime.now() # Using local time same as updated_at
                            for b in changes['BookingRequest']:
                                # We only want to alert if it's PENDING and very RECENT (last 10 mins)
                                # This prevents history pulls from screaming
                                if b.get('status', '').lower() == 'pending':
                                    try:
                                        # Parse created_at or updated_at
                                        ts_str = b.get('created_at') or b.get('updated_at')
                                        if ts_str:
                                            # Strip timezone if present
                                            clean_ts = ts_str.split('.')[0].replace('T', ' ').replace('Z', '')
                                            dt = datetime.fromisoformat(clean_ts)
                                            # If created in last 10 minutes (600 seconds)
                                            if abs((now - dt).total_seconds()) < 600:
                                                has_real_new = True
                                                break
                                    except: continue
                        except Exception as e:
                            logger.error(f"Error checking newness: {e}")
                            
                        if has_real_new:
                            logger.info("REAL new booking detected! Triggering alert.")
                            self.trigger_booking_alert()

                # CRITICAL: Use server_time if provided to avoid local clock drift issues skipping records
                if server_time:
                    config['last_cloud_sync'] = server_time
                else:
                    # Fallback to local time if bridge doesn't provide it
                    new_ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    config['last_cloud_sync'] = new_ts
                
                node_config.save_config(config)
                
        except Exception as e:
            logger.error(f"Network error pulling changes: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def trigger_booking_alert(self):
        """Sets a flag or sends a signal for the UI to play sound/show toast."""
        # We can store this in a static variable or a local config that the dashboard polls
        try:
            conn = get_db_connection()
            # Mark that a new booking alert is pending
            conn.execute(
                "INSERT OR REPLACE INTO app_settings (setting_name, setting_value) VALUES (?, ?)",
                ('pending_booking_alert', 'true')
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error setting booking alert flag: {e}")

# Global instance
sync_manager = AutomatedSyncManager()

def trigger_sync_immediate():
    """Immediately trigger a sync cycle (e.g. after a Save operation)."""
    threading.Thread(target=sync_manager.run_automated_sync, daemon=True).start()

# ==========================================
# API ENDPOINTS (Local Integration)
# ==========================================

def login_required_local(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'logged_in' not in session:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function

@sync_bp.route('/check_alerts')
@login_required_local
def check_alerts():
    """Endpoint for the dashboard to poll for real-time notifications."""
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'pending_booking_alert'").fetchone()
        
        has_alert = False
        if row and row['setting_value'] == 'true':
            has_alert = True
            # Reset the flag after reading
            conn.execute("UPDATE app_settings SET setting_value = 'false' WHERE setting_name = 'pending_booking_alert'")
            conn.commit()
            
        conn.close()
        return jsonify({"new_booking": has_alert})
    except:
        return jsonify({"new_booking": False})
@sync_bp.route('/status')
@login_required_local
def get_sync_status():
    """Returns the current sync status for the UI."""
    config = node_config.load_config()
    return jsonify({
        "last_sync": config.get('last_cloud_sync'),
        "enabled": config.get('sync_enabled'),
        "cloud_url": config.get('cloud_api_url')
    })

@sync_bp.route('/trigger', methods=['POST'])
@login_required_local
def manual_trigger():
    """Manual trigger to start a sync cycle immediately."""
    try:
        trigger_sync_immediate()
        return jsonify({"status": "success", "message": "Synchronization triggered."})
    except Exception as e:
        logger.error(f"Manual sync trigger error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@sync_bp.route('/push', methods=['POST'])
def receive_push():
    """Endpoint for other nodes to push data directly to this node."""
    try:
        data = request.get_json()
        table = data.get('table')
        records = data.get('records', [])
        api_key = data.get('api_key')
        
        config = node_config.load_config()
        if api_key != config.get('cloud_api_key'):
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
            
        applied = apply_incoming_changes({table: records})
        return jsonify({"status": "success", "applied": applied})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@sync_bp.route('/pull', methods=['POST'])
def handle_pull():
    """Endpoint for other nodes to pull data from this node."""
    try:
        data = request.get_json()
        last_sync = data.get('last_sync_timestamp', '1970-01-01 00:00:00')
        api_key = data.get('api_key')
        
        config = node_config.load_config()
        if api_key != config.get('cloud_api_key'):
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
            
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        changes = {}
        total_count = 0
        
        for table in SYNC_TABLES:
            # Simple query to find records changed since last sync
            rows = conn.execute(f"SELECT * FROM {table} WHERE updated_at > ?", (last_sync,)).fetchall()
            if rows:
                changes[table] = [dict(r) for r in rows]
                total_count += len(rows)
        conn.close()
        
        return jsonify({"status": "success", "changes": changes, "count": total_count, "server_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# MERGE ENGINE (LWW)
# ==========================================

def apply_incoming_changes(changes):
    """Applies changes from cloud to local database."""
    if not changes: return 0
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        processed = 0
        for table, records in changes.items():
            # Support all tables in sync list
            if table not in SYNC_TABLES: 
                # Log if unexpected table found
                logger.warning(f"Skipping unknown table from cloud: {table}")
                continue
                
            for r in records:
                try:
                    # GTEC Privacy Preservation on Pull (DISABLED -Preserving full names for node consistency)
                    # if table == 'Student' and 'name' in r:
                    #     from app import name_to_initials
                    #     r['name'] = name_to_initials(r['name'])
                    # elif table == 'BookingRequest' and 'full_name' in r:
                    #     from app import name_to_initials
                    #     r['full_name'] = name_to_initials(r['full_name'])

                    merge_record(cursor, table, r)
                    processed += 1
                except Exception as e:
                    logger.error(f"Error merging record into {table}: {e}")
        conn.commit()
        return processed
    except Exception as e:
        logger.error(f"Failed to apply incoming changes: {e}")
        return 0
    finally:
        conn.close()

def get_conflict_key(table):
    """Determines the unique identifier for a table's sync logic."""
    if table == 'app_settings': return 'setting_name'
    if table == 'BookingRequest': return 'reference'
    return 'global_id'

def merge_record(cursor, table, remote_record):
    """Last Write Wins merge logic using the appropriate key for each table."""
    key_field = get_conflict_key(table)
    key_value = remote_record.get(key_field)
    
    if not key_value: 
        logger.debug(f"Skipping record in {table} with missing key {key_field}")
        return

    # Check local version
    query = f"SELECT updated_at FROM {table} WHERE {key_field} = ?"
    local = cursor.execute(query, (key_value,)).fetchone()
    
    should_apply = False
    if local is None:
        should_apply = True
    else:
        # Remote is newer than local (using string comparison for ISO timestamps)
        remote_ts = remote_record.get('updated_at', '1970-01-01 00:00:00')
        local_ts = local[0] or '1970-01-01 00:00:00'
        if remote_ts > local_ts:
            should_apply = True

    if should_apply:
        # Get local columns to avoid "no such column" errors
        cursor.execute(f"PRAGMA table_info({table})")
        local_cols = [c[1] for c in cursor.fetchall()]
        
        # Filter columns to only those that exist in our local database
        cols = [k for k in remote_record.keys() if k in local_cols and k != 'id']
        values = [remote_record[k] for k in cols]
        
        if not cols: return
        
        placeholders = ", ".join(["?"] * len(cols))
        update_stmt = ", ".join([f"{c} = excluded.{c}" for c in cols if c != key_field])
        
        # SQLite Upsert
        upsert_query = f"""
            INSERT INTO {table} ({', '.join(cols)}) 
            VALUES ({placeholders}) 
            ON CONFLICT({key_field}) DO UPDATE SET {update_stmt}
        """
        cursor.execute(upsert_query, values)
        # Ensure 'last_synced_at' is marked as current so we don't push back what we just pulled
        if 'last_synced_at' in cols:
            idx = cols.index('last_synced_at')
            # Update the record in DB to match current sync time
            cursor.execute(f"UPDATE {table} SET last_synced_at = ? WHERE {key_field} = ?", 
                          (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), key_value))
