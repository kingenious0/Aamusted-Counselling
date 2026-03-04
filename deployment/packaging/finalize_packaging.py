import shutil
import os

def zip_distributions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(base_dir, "AAMUSTED_Universal_Distribution")
    
    mac_dist = os.path.join(dist_root, "AAMUSTED_Mac_Version")
    win_dist = os.path.join(dist_root, "Windows_Version")
    
    print(f"Checking distribution folder: {dist_root}")
    
    # Zip Mac
    if os.path.exists(mac_dist):
        print("Folder found. Zipping Mac Version...")
        zip_path = os.path.join(dist_root, "AAMUSTED_Mac_Installer")
        shutil.make_archive(zip_path, 'zip', mac_dist)
        print(f"✅ Created Mac Installer: {zip_path}.zip")
    else:
        print("❌ Mac Version folder not found!")

    # Zip Windows
    if os.path.exists(win_dist):
        print("Folder found. Zipping Windows Version...")
        zip_path = os.path.join(dist_root, "AAMUSTED_Windows_Installer")
        shutil.make_archive(zip_path, 'zip', win_dist)
        print(f"✅ Created Windows Installer: {zip_path}.zip")
    else:
        print("❌ Windows Version folder not found!")

if __name__ == "__main__":
    zip_distributions()
