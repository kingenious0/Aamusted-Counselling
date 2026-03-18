import sqlite3
import json
import requests
import threading
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
import node_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyncEngine")

# Create Blueprint
sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

# Tables to sync
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
            
            # Wait for next cycle (default 60 seconds)
            config = node_config.load_config()
            interval = config.get('sync_interval_seconds', 60)
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

        # 1. PUSH local changes (where updated_at > last_synced_at)
        self.push_pending_changes(cloud_url, api_key)

        # 2. PULL remote changes (specifically new BookingRequests)
        self.pull_remote_changes(cloud_url, api_key)

    def push_pending_changes(self, cloud_url, api_key):
        """Finds all records changed locally and pushes them to cloud."""
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

                logger.info(f"Syncing {len(pending)} records for table {table}...")
                
                # Push in batches if necessary, but here we push all for simplicity
                changes = {table: [dict(r) for r in pending]}
                
                try:
                    resp = requests.post(
                        f"{cloud_url}/push", 
                        json={"changes": changes, "api_key": api_key, "node_id": node_config.get_node_id()},
                        timeout=15
                    )
                    
                    if resp.status_code == 200:
                        # Mark as synced locally
                        sync_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                        for record in pending:
                            cursor.execute(
                                f"UPDATE {table} SET last_synced_at = ? WHERE global_id = ?",
                                (sync_timestamp, record['global_id'])
                            )
                        conn.commit()
                        logger.info(f"Successfully pushed {len(pending)} records from {table}")
                    else:
                        logger.warning(f"Failed to push {table}: {resp.text}")
                except Exception as e:
                    logger.error(f"Network error pushing {table}: {e}")
                    
        finally:
            conn.close()

    def pull_remote_changes(self, cloud_url, api_key):
        """Pulls changes from cloud to local (e.g. new BookingRequests)."""
        config = node_config.load_config()
        last_pull_ts = config.get('last_cloud_sync', '1970-01-01 00:00:00')
        
        try:
            resp = requests.post(
                f"{cloud_url}/pull", 
                json={
                    "last_sync_timestamp": last_pull_ts, 
                    "api_key": api_key, 
                    "node_id": node_config.get_node_id()
                },
                timeout=15
            )
            
            if resp.status_code == 200:
                data = resp.json()
                changes = data.get('changes', {})
                count = data.get('count', 0)
                
                if count > 0:
                    apply_incoming_changes(changes)
                    logger.info(f"Pulled {count} changes from cloud.")
                    
                    # If there are new BookingRequests, we might want to trigger a frontend alert
                    if 'BookingRequest' in changes:
                        self.trigger_booking_alert()

                # Update sync timestamp
                new_ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                config['last_cloud_sync'] = new_ts
                node_config.save_config(config)
                
        except Exception as e:
            logger.error(f"Network error pulling changes: {e}")

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

@sync_bp.route('/check_alerts')
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
def get_sync_status():
    """Returns the current sync status for the UI."""
    config = node_config.load_config()
    return jsonify({
        "last_sync": config.get('last_cloud_sync'),
        "enabled": config.get('sync_enabled'),
        "cloud_url": config.get('cloud_api_url')
    })

# ==========================================
# MERGE ENGINE (LWW)
# ==========================================

def apply_incoming_changes(changes):
    """Applies changes from cloud to local database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        processed = 0
        for table, records in changes.items():
            if table not in SYNC_TABLES: continue
            for r in records:
                merge_record(cursor, table, r)
                processed += 1
        conn.commit()
        return processed
    finally:
        conn.close()

def merge_record(cursor, table, remote_record):
    """Last Write Wins merge logic."""
    global_id = remote_record.get('global_id')
    if not global_id: return

    local = cursor.execute(f"SELECT updated_at, last_synced_at FROM {table} WHERE global_id = ?", (global_id,)).fetchone()
    
    should_apply = False
    is_insert = False

    if local is None:
        should_apply = True
        is_insert = True
    else:
        # Remote is newer than local
        remote_ts = remote_record.get('updated_at', '1970-01-01 00:00:00')
        local_ts = local[0] or '1970-01-01 00:00:00'
        if remote_ts > local_ts:
            should_apply = True
            is_insert = False

    if should_apply:
        # Prepare columns (skip local 'id')
        cols = [k for k in remote_record.keys() if k != 'id']
        # Ensure 'last_synced_at' is marked as current so we don't push back what we just pulled
        if 'last_synced_at' in remote_record:
            remote_record['last_synced_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        placeholders = ', '.join(['?'] * len(cols))
        col_names = ', '.join(cols)
        values = [remote_record[k] for k in cols]

        if is_insert:
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
        else:
            set_clause = ', '.join([f"{col}=?" for col in cols])
            query = f"UPDATE {table} SET {set_clause} WHERE global_id=?"
            values.append(global_id)
            cursor.execute(query, values)
