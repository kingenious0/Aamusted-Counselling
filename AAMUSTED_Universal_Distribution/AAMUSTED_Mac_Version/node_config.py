import json
import os
import uuid
import sys

CONFIG_FILE = 'node_config.json'

def get_config_path():
    """Get config path - works in both dev and EXE mode"""
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, CONFIG_FILE)

def load_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return create_default_config()
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return create_default_config()

def create_default_config():
    """Create a default config with a random Node ID"""
    config = {
        "node_id": f"NODE_{str(uuid.uuid4())[:8].upper()}",
        "node_role": "Unassigned", # e.g., 'SECRETARY', 'COUNSELLOR'
        "peer_ip": "", # Manual IP entry for the 'other' machine
        "sync_enabled": True,
        "sync_interval_seconds": 60
    }
    save_config(config)
    return config

def save_config(config):
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Config saved to {config_path}")
    except Exception as e:
        print(f"Error saving config: {e}")

def get_node_id():
    config = load_config()
    return config.get('node_id')

def get_peer_ip():
    config = load_config()
    return config.get('peer_ip')
