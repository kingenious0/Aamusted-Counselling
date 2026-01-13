import zipfile
import re
import os

def extract_all_text(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        full_content = []
        with zipfile.ZipFile(file_path) as docx:
            # List of XML files that might contain text
            target_xmls = ['word/document.xml', 'word/footnotes.xml', 'word/endnotes.xml']
            
            for xml_name in target_xmls:
                if xml_name in docx.namelist():
                    print(f"--- Extracting from {xml_name} ---")
                    xml_content = docx.read(xml_name).decode('utf-8', errors='ignore')
                    # Find all text inside <w:t> tags
                    matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
                    text_segment = " ".join(matches)
                    full_content.append(text_segment)
                    text_segment = " ".join(matches)
                    full_content.append(text_segment)
            
            with open('extracted_report.txt', 'w', encoding='utf-8') as f:
                f.write("\n\n".join(full_content))
            print("Text saved to extracted_report.txt")
            
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    path = r"C:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\Counseling System Project Report- Group 6.docx"
    extract_all_text(path)
