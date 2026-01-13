import zipfile
import os

def inspect_docx_structure(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with zipfile.ZipFile(file_path) as docx:
            print("Files in archive:")
            for info in docx.infolist():
                print(f"- {info.filename} ({info.file_size} bytes)")
                
            print("\n--- Snippet of word/document.xml (first 1000 chars) ---")
            xml_content = docx.read('word/document.xml')
            print(xml_content[:1000].decode('utf-8', errors='ignore'))
            
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    path = r"C:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\Counseling System Project Report- Group 6.docx"
    inspect_docx_structure(path)
