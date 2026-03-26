import os

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_logic = """def name_to_initials(name_input):
    if not name_input: return "N/A"
    import re
    # Preserve numeric ID suffix if present: e.g. \"A. (14)\"
    suffix = \"\"
    match_id = re.search(r'\\s*\\(\\d+\\)$', str(name_input))
    if match_id:
        suffix = match_id.group(0)
        name_input = str(name_input)[:match_id.start()]
    
    # Standardize to initials (E.M.)
    raw = str(name_input).replace('.', ' ').strip()
    parts = [p.strip() for p in raw.split() if p.strip()]
    letters = [p[0].upper() for p in parts if p and p[0].isalpha()]
    
    if not letters:
        return str(name_input)[:2].upper() + suffix
        
    return \".\".join(letters) + \".\" + suffix
"""

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'def name_to_initials' in line:
        start_idx = i
        # Find the return line
        for j in range(i+1, i+20):
            if 'return' in lines[j] and 'letters' in lines[j]:
                end_idx = j
                break
        break

if start_idx != -1 and end_idx != -1:
    lines[start_idx:end_idx+1] = [new_logic + '\n']
    with open(app_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Sucessfully updated initials logic in app.py")
else:
    print(f"Failed to find target lines (start: {start_idx}, end: {end_idx})")
