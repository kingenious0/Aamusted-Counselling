import os
os.makedirs("static/js", exist_ok=True)
js = """// AAMUSTED GCC - Offline IndexedDB Module
const DB_NAME = ""AAMUSTED_GCC_OFFLINE_DB"";
"""
open("static/js/db.js","w").write(js)
print("done")