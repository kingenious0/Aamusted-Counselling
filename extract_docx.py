import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_docx(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with zipfile.ZipFile(file_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # Namespace for Word
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            full_text = []
            
            # Iterate through paragraphs
            for p in tree.findall('.//w:p', ns):
                para_text = []
                # Iterate through runs in the paragraph
                for r in p.findall('.//w:r', ns):
                    # Iterate through text elements in the run
                    for t in r.findall('.//w:t', ns):
                        if t.text:
                            para_text.append(t.text)
                
                # Join runs to header paragraph text
                if para_text:
                    full_text.append(''.join(para_text))
            
            # Print joined text with newlines
            print('\n'.join(full_text))
            
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    path = r"C:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\Counseling System Project Report- Group 6.docx"
    extract_text_from_docx(path)
