import os
import shutil
import subprocess
import zipfile
import sys

def zip_folder(folder_path, output_path):
    print(f"Zipping {folder_path} to {output_path}...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

import stat

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(base_dir, 'AAMUSTED_Universal_Distribution')
    windows_dist_dir = os.path.join(dist_root, 'AAMUSTED_Windows_Installer')
    mac_dist_dir = os.path.join(dist_root, 'AAMUSTED_Mac_Version')

    # 1. Build Windows EXE
    print("Building Windows EXE...")
    try:
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'AAMUSTED_Counseling_System.spec', '--clean', '--noconfirm'])
    except subprocess.CalledProcessError as e:
        print(f"Error building EXE: {e}")
        return

    # 2. Copy EXE to Windows Distribution Folder
    print("Updating Windows Distribution...")
    exe_source = os.path.join(base_dir, 'dist', 'AAMUSTED_Counseling_System.exe')
    exe_dest = os.path.join(windows_dist_dir, 'AAMUSTED_Counseling_System.exe')
    
    if os.path.exists(exe_source):
        if os.path.exists(exe_dest):
            os.remove(exe_dest)
        shutil.copy2(exe_source, exe_dest)
        print(f"Copied {exe_source} to {exe_dest}")
    else:
        print("Error: Compiled EXE not found!")
        return

    # 3. Update Mac Source Distribution
    print("Updating Mac Distribution...")
    files_to_copy = [
        'app.py', 
        'db_setup.py', 
        'sync_engine.py', 
        'node_config.py',
        'force_db_fix.py',
        'aamusted system_logo.png'
    ]
    folders_to_copy = ['templates', 'static']

    for f in files_to_copy:
        src = os.path.join(base_dir, f)
        dst = os.path.join(mac_dist_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Updated {f}")

    for folder in folders_to_copy:
        src = os.path.join(base_dir, folder)
        dst = os.path.join(mac_dist_dir, folder)
        if os.path.exists(dst):
            shutil.rmtree(dst, onerror=remove_readonly)
        shutil.copytree(src, dst)
        print(f"Updated {folder}/")

    # 4. Create ZIPs
    print("Creating Archives...")
    zip_folder(windows_dist_dir, os.path.join(dist_root, 'AAMUSTED_Windows_Installer.zip'))
    zip_folder(mac_dist_dir, os.path.join(dist_root, 'AAMUSTED_Mac_Installer.zip'))

    print("Success! Distribution updated.")

if __name__ == "__main__":
    main()
