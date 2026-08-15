import sys, os
cloud_bridge_dir = os.path.join(os.path.dirname(__file__), '..', 'cloud_bridge')
sys.path.insert(0, cloud_bridge_dir)
from bridge_app import app
