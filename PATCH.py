#!/usr/bin/env python3
"""
=============================================================
  AAMUSTED COUNSELLING SYSTEM - UNIVERSAL PATCH v2.0
=============================================================
  Run this ONCE on any installed machine to apply:
    [+] All latest code & bug fixes from GitHub
    [+] Full Offline UI (Bootstrap, Icons, SweetAlert2)
    [+] Silent Auto-Updater (future updates = zero effort!)

  HOW TO RUN:
    1. Copy this file to the system's root folder
       (the folder that contains app.py and counseling.db)
    2. Open a terminal/command prompt in that folder
    3. Run: python PATCH.py
=============================================================
"""

import os
import sys
import shutil
import zipfile
import io
import json
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
REPO_OWNER = "kingenious0"
REPO_NAME = "Aamusted-Counselling"
BRANCH = "main"
GITHUB_ZIP_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/{BRANCH}.zip"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{BRANCH}"

# Files/folders that must NEVER be overwritten
PROTECTED = {
    'counseling.db',
    'node_config.json',
    'current_sha.txt',
    '.git',
    '_update_temp',
    'PATCH.py',       # Don't overwrite ourselves
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────


def banner(text, char='=', width=62):
    print(char * width)
    print(f"  {text}")
    print(char * width)


def step(n, total, text):
    print(f"\n[{n}/{total}] {text}...")


def ok(text):
    print(f"    ✓ {text}")


def warn(text):
    print(f"    ! {text}")


def fail(text):
    print(f"    ✗ ERROR: {text}")


def find_system_dir():
    """Locate the system root — where app.py and counseling.db live."""
    # 1. Try current working directory
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, 'app.py')):
        return cwd

    # 2. Try script's own directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, 'app.py')):
        return script_dir

    # 3. Search Desktop / Documents / common install locations
    home = os.path.expanduser("~")
    search_roots = [
        os.path.join(home, 'Desktop'),
        os.path.join(home, 'Documents'),
        'C:\\',
        'D:\\',
    ]
    for root in search_roots:
        if not os.path.exists(root):
            continue
        try:
            for entry in os.scandir(root):
                if entry.is_dir():
                    candidate = os.path.join(entry.path, 'app.py')
                    if os.path.exists(candidate):
                        return entry.path
        except PermissionError:
            continue

    return None


def get_requests():
    """Return requests module — prefers installed, falls back to urllib."""
    try:
        import requests
        return requests
    except ImportError:
        pass

    # Minimal shim using urllib so we never fail on missing requests
    import urllib.request
    import urllib.error

    class _FakeResponse:
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content

        def json(self):
            return json.loads(self.content.decode())

    class _FakeRequests:
        UA = 'AAMUSTED-Patcher/2.0'

        def get(self, url, headers=None, timeout=30):
            req = urllib.request.Request(url, headers={'User-Agent': self.UA})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return _FakeResponse(r.status, r.read())
            except urllib.error.HTTPError as e:
                return _FakeResponse(e.code, b'')

    return _FakeRequests()

# ─── MAIN PATCH ──────────────────────────────────────────────────────────────


def main():
    print()
    banner("AAMUSTED COUNSELLING SYSTEM — UNIVERSAL PATCH v2.0")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    TOTAL_STEPS = 5
    req = get_requests()

    # ── STEP 1: Find system directory ────────────────────────────────────────
    step(1, TOTAL_STEPS, "Locating system installation")
    system_dir = find_system_dir()
    if not system_dir:
        fail(
            "Could not locate the system folder (app.py not found).\n"
            "    Please copy PATCH.py into the same folder as app.py and try again."
        )
        sys.exit(1)
    ok(f"Found at: {system_dir}")

    sha_file = os.path.join(system_dir, 'current_sha.txt')
    temp_dir = os.path.join(system_dir, '_update_temp')

    # Read current SHA
    old_sha = "unknown"
    if os.path.exists(sha_file):
        with open(sha_file, 'r') as f:
            old_sha = f.read().strip()
    ok(f"Current version SHA: {old_sha[:8] if old_sha != 'unknown' else 'unknown'}")

    # ── STEP 2: Fetch latest SHA from GitHub ─────────────────────────────────
    step(2, TOTAL_STEPS, "Checking latest version on GitHub")
    try:
        api_resp = req.get(
            GITHUB_API_URL,
            headers={'User-Agent': 'AAMUSTED-Patcher/2.0'},
            timeout=15
        )
        if api_resp.status_code != 200:
            raise ConnectionError(
                f"GitHub API returned HTTP {api_resp.status_code}")
        new_sha = api_resp.json().get('sha', '')
        if not new_sha:
            raise ValueError("Could not read SHA from GitHub API response")
        ok(f"Latest GitHub SHA: {new_sha[:8]}")
    except Exception as e:
        fail(
            f"Cannot reach GitHub — check internet connection.\n    Detail: {e}")
        sys.exit(1)

    # ── STEP 3: Download the update ZIP ──────────────────────────────────────
    step(3, TOTAL_STEPS, "Downloading latest version from GitHub")
    try:
        print(f"    Downloading {GITHUB_ZIP_URL}")
        zip_resp = req.get(
            GITHUB_ZIP_URL,
            headers={'User-Agent': 'AAMUSTED-Patcher/2.0'},
            timeout=120
        )
        if zip_resp.status_code != 200:
            raise ConnectionError(
                f"Download failed — HTTP {zip_resp.status_code}")
        size_kb = len(zip_resp.content) / 1024
        ok(f"Downloaded ({size_kb:.0f} KB)")
    except Exception as e:
        fail(f"Download failed: {e}")
        sys.exit(1)

    # ── STEP 4: Extract & Apply ───────────────────────────────────────────────
    step(4, TOTAL_STEPS, "Applying update (protected files kept safe)")

    # Clean temp dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        z = zipfile.ZipFile(io.BytesIO(zip_resp.content))
        z.extractall(temp_dir)
    except Exception as e:
        fail(f"Could not extract ZIP: {e}")
        sys.exit(1)

    # The ZIP extracts into a subfolder like 'Aamusted-Counselling-main'
    extracted_contents = os.listdir(temp_dir)
    if not extracted_contents:
        fail("ZIP was empty or corrupt.")
        sys.exit(1)
    source_root = os.path.join(temp_dir, extracted_contents[0])

    copied = 0
    skipped = []
    errors = []

    for item in os.listdir(source_root):
        if item in PROTECTED:
            skipped.append(item)
            continue

        src = os.path.join(source_root, item)
        dst = os.path.join(system_dir, item)

        try:
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            errors.append(f"{item}: {e}")

    ok(f"Applied {copied} item(s)")
    if skipped:
        ok(f"Protected (untouched): {', '.join(skipped)}")
    if errors:
        for err in errors:
            warn(f"Could not copy {err}")

    # Write new SHA
    try:
        with open(sha_file, 'w') as f:
            f.write(new_sha)
        ok(f"Version updated: {old_sha[:8]} → {new_sha[:8]}")
    except Exception as e:
        warn(f"Could not write SHA file: {e}")

    # Cleanup temp
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    # ── STEP 5: Verify key offline files ─────────────────────────────────────
    step(5, TOTAL_STEPS, "Verifying offline UI assets")
    offline_checks = {
        'Bootstrap CSS':    os.path.join(system_dir, 'static', 'css', 'bootstrap.min.css'),
        'Bootstrap Icons':  os.path.join(system_dir, 'static', 'css', 'bootstrap-icons.css'),
        'Bootstrap JS':     os.path.join(system_dir, 'static', 'js', 'bootstrap.bundle.min.js'),
        'SweetAlert2':      os.path.join(system_dir, 'static', 'js', 'sweetalert2.all.min.js'),
        'Modern Theme CSS': os.path.join(system_dir, 'static', 'css', 'modern_theme.css'),
    }
    all_ok = True
    for name, path in offline_checks.items():
        if os.path.exists(path):
            ok(f"{name} — present ✓")
        else:
            warn(f"{name} — MISSING (UI may need internet for this asset)")
            all_ok = False

    if not all_ok:
        print()
        warn("Some offline UI assets are missing. The system may still work")
        warn("with internet. Push those static files to GitHub to fix this.")

    # ── DONE ──────────────────────────────────────────────────────────────────
    print()
    banner("PATCH COMPLETE!", char='*')
    print(f"  Version: {new_sha[:12]}")
    print(f"  Date:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("  WHAT TO DO NEXT:")
    print("  1. Restart the system (it will restart automatically on next boot)")
    print("  2. The system will now auto-update silently on every startup")
    print("  3. No more manual patches needed — ever!")
    print()
    print("  Thank you for using AAMUSTED Counselling System.")
    print('=' * 62)
    print()

    # Prompt to restart Flask if it looks like it's running
    try:
        import subprocess
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True, text=True, timeout=5
        )
        port_in_use = ':5000' in result.stdout
    except Exception:
        port_in_use = False

    if port_in_use:
        print("  ⚠  The system appears to be running on port 5000.")
        print("     Please RESTART the system for the update to take effect.")
        print()

    input("  Press ENTER to close this window...")


if __name__ == "__main__":
    main()
