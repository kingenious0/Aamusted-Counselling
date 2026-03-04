import sqlite3
import json
import requests
from flask import Blueprint, request, jsonify
from datetime import datetime
import node_config

# Create Blueprint
sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

# Tables to sync
SYNC_TABLES = [
    'Student', 'Appointment', 'session', 'Referral', 
    'CaseManagement', 'OutcomeQuestionnaire', 'DASS21', 
    'Feedback', 'SessionIssue', 'Notification',
    'app_settings'
]

def get_db_connection():
    # Helper to get DB connection (reused logic)
    import app
    return app.get_db_connection()

# ==========================================
# API ENDPOINTS (Server Side)
# ==========================================

@sync_bp.route('/handshake', methods=['POST'])
def handshake():
    """Verify connection and return node info."""
    config = node_config.load_config()
    return jsonify({
        "status": "ok",
        "node_id": config.get('node_id'),
        "role": config.get('node_role'),
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    })

@sync_bp.route('/pull', methods=['POST'])
def pull_changes():
    """
    Peer is asking for our changes since a specific timestamp.
    Input: { "last_sync_timestamp": "2024-01-01..." }
    """
    data = request.json
    last_sync = data.get('last_sync_timestamp', '1970-01-01 00:00:00')
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    changes = {}
    
    try:
        total_count = 0
        for table in SYNC_TABLES:
            # Get records updated since last_sync
            # Logic: updated_at > last_sync
            query = f"SELECT * FROM {table} WHERE updated_at > ?"
            rows = cursor.execute(query, (last_sync,)).fetchall()
            
            table_changes = []
            for row in rows:
                # Convert row to dict
                record = dict(row)
                table_changes.append(record)
            
            if table_changes:
                changes[table] = table_changes
                total_count += len(table_changes)
                
        return jsonify({
            "status": "success",
            "changes": changes,
            "count": total_count,
            "node_id": node_config.get_node_id()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

@sync_bp.route('/push', methods=['POST'])
def receive_push():
    """
    Peer is sending us their changes. We need to merge them.
    Input: { "changes": { "Student": [ ... ] } }
    """
    data = request.json
    changes = data.get('changes', {})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    processed_count = 0
    errors = []
    
    try:
        for table, records in changes.items():
            if table not in SYNC_TABLES:
                continue
                
            for record in records:
                try:
                    merge_record(cursor, table, record)
                    processed_count += 1
                except Exception as e:
                    errors.append(f"Error processing {table} record {record.get('global_id')}: {str(e)}")
        
        conn.commit()
        return jsonify({
            "status": "success",
            "processed": processed_count,
            "errors": errors
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

def merge_record(cursor, table, remote_record):
    """
    LWW (Last Write Wins) Merge Logic
    """
    global_id = remote_record.get('global_id')
    if not global_id:
        return # Skip invalid records
    
    # 1. Check if we have this record
    local_record = cursor.execute(f"SELECT updated_at FROM {table} WHERE global_id = ?", (global_id,)).fetchone()
    
    should_update = False
    
    if local_record is None:
        # INSERT
        should_update = True
        is_insert = True
    else:
        # UPDATE if remote is newer
        local_updated_at = local_record[0]
        remote_updated_at = remote_record.get('updated_at')
        
        if remote_updated_at > local_updated_at:
            should_update = True
            is_insert = False
    
    if should_update:
        # Construct INSERT OR REPLACE query
        # We filter out 'id' (local PK) because it might conflict or allow auto-increment
        # Actually, for INSERT, we ignore 'id' and let local DB generate it
        # For UPDATE, we find by global_id
        
        cols = [k for k in remote_record.keys() if k != 'id']
        placeholders = ', '.join(['?'] * len(cols))
        col_names = ', '.join(cols)
        
        values = [remote_record[k] for k in cols]
        
        if is_insert:
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
        else:
            # Dynamic Update
            set_clause = ', '.join([f"{col}=?" for col in cols])
            query = f"UPDATE {table} SET {set_clause} WHERE global_id=?"
            values.append(global_id)
            cursor.execute(query, values)

# ==========================================
# CLIENT LOGIC (Client Side)
# ==========================================

def trigger_sync():
    """
    Called periodically or manually to run a sync cycle.
    """
    config = node_config.load_config()
    peer_ip = config.get('peer_ip')
    
    if not peer_ip:
        return {"status": "skipped", "message": "No peer IP configured"}
    
    peer_url = f"http://{peer_ip}:5000/api/sync"
    
    # 1. Handshake
    try:
        resp = requests.post(f"{peer_url}/handshake", timeout=2)
        if resp.status_code != 200:
            return {"status": "error", "message": "Handshake failed"}
    except Exception as e:
        return {"status": "offline", "message": f"Peer unreachable: {str(e)}"}
        
    # 2. Pull (Get their changes)
    # We need to know when we last synced with THEM.
    # For simplicity, we can store 'last_sync_time' in config or DB.
    last_sync = config.get(f'last_sync_with_{peer_ip}', '1970-01-01 00:00:00')
    
    try:
        print(f"Pulling changes since {last_sync}...")
        pull_resp = requests.post(f"{peer_url}/pull", json={"last_sync_timestamp": last_sync}, timeout=10)
        pull_data = pull_resp.json()
        
        if pull_data['status'] == 'success' and pull_data['count'] > 0:
            # Apply their changes locally using OUR push logic (reusing local API or direct function)
            # Better to call the function directly
            
            # Since we are running in the same app context, we can misuse the 'receive_push' logic 
            # OR refactor merge_record to be usable directly.
            # Let's call the local API helper manually or refactor.
            # I will refactor 'receive_push' logic into a helper 'apply_incoming_changes'.
            
            apply_incoming_changes(pull_data['changes'])
            print(f"Applied {pull_data['count']} incoming changes.")
            
        # Update last sync time
        config[f'last_sync_with_{peer_ip}'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        node_config.save_config(config)
        
    except Exception as e:
        print(f"Error during PULL: {e}")
        return {"status": "error", "message": f"Pull failed: {e}"}

    # 3. Push (Send our changes)
    # This is tricky: we only want to send changes THEY haven't seen.
    # But simpler: just send everything changed since last sync time.
    # Same timestamp 'last_sync' applies.
    
    try:
        # Get local changes
        local_changes = get_local_changes(last_sync)
        if local_changes:
            print(f"Pushing {sum(len(v) for v in local_changes.values())} records...")
            requests.post(f"{peer_url}/push", json={"changes": local_changes}, timeout=10)
    except Exception as e:
        print(f"Error during PUSH: {e}")

    return {"status": "success", "message": "Sync completed"}

def apply_incoming_changes(changes):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for table, records in changes.items():
            if table not in SYNC_TABLES: continue
            for r in records:
                merge_record(cursor, table, r)
        conn.commit()
    finally:
        conn.close()

def get_local_changes(timestamp):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    changes = {}
    total = 0
    try:
        for table in SYNC_TABLES:
            rows = cursor.execute(f"SELECT * FROM {table} WHERE updated_at > ?", (timestamp,)).fetchall()
            if rows:
                changes[table] = [dict(r) for r in rows]
                total += len(rows)
    finally:
        conn.close()
    return changes if total > 0 else None
