import zipfile
import re
import os

def extract_text_regex(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with zipfile.ZipFile(file_path) as docx:
            xml_content = docx.read('word/document.xml').decode('utf-8')
            # Find all text inside <w:t> tags
            matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
            print(" ".join(matches))
            
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    path = r"C:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\Counseling System Project Report- Group 6.docx"
    extract_text_regex(path)
