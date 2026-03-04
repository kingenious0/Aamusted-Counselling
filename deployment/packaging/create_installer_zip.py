
import os
import zipfile
import shutil

def create_mac_installer_zip():
    base_dir = "AAMUSTED_Universal_Distribution/AAMUSTED_Mac_Version"
    output_filename = "AAMUSTED_Mac_Installer_FIXED.zip"
    
    # Ensure the base directory exists
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} not found!")
        return

    print(f"Creating {output_filename} from {base_dir}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                # Skip unnecessary files
                if file == ".DS_Store" or file.endswith(".pyc"):
                    continue
                
                file_path = os.path.join(root, file)
                
                # Calculate archive name (relative to base_dir)
                archive_name = os.path.relpath(file_path, base_dir)
                
                # We want the root of the zip to contain the files directly, or inside a folder?
                # Usually mac installers are a folder. Let's put them inside "AAMUSTED_Mac_Installer" folder
                archive_name = os.path.join("AAMUSTED_Mac_Installer", archive_name)
                
                print(f"Adding {archive_name}...")
                zipf.write(file_path, archive_name)
    
    print(f"Successfully created {output_filename}")

if __name__ == "__main__":
    create_mac_installer_zip()
