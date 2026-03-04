import os
import zipfile
import shutil
import time

def zip_folder(folder_path, output_path):
    print(f"Zipping {folder_path}...")
    try:
        if os.path.exists(output_path):
            os.remove(output_path)
            
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
                        # print(f"  Added {arcname}")
                    except Exception as e:
                        print(f"  Error adding {file}: {e}")
        print(f"Created {output_path}")
    except Exception as e:
        print(f"Failed to create zip {output_path}: {e}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(base_dir, 'AAMUSTED_Universal_Distribution')
    
    # Define paths
    win_dist = os.path.join(dist_root, 'AAMUSTED_Windows_Installer')
    mac_dist = os.path.join(dist_root, 'AAMUSTED_Mac_Version')
    
    win_zip = os.path.join(dist_root, 'AAMUSTED_Windows_Installer.zip')
    mac_zip = os.path.join(dist_root, 'AAMUSTED_Mac_Installer.zip')

    # Verify contents existence before zipping
    if os.path.exists(os.path.join(win_dist, 'AAMUSTED_Counseling_System.exe')):
        print("Windows EXE found. Zipping...")
        zip_folder(win_dist, win_zip)
    else:
        print("Warning: Windows EXE not found in dist folder.")

    if os.path.exists(os.path.join(mac_dist, 'app.py')):
        print("Mac Source found. Zipping...")
        zip_folder(mac_dist, mac_zip)
    else:
        print("Warning: Mac App source not found.")

if __name__ == "__main__":
    main()
