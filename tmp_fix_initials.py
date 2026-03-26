"""Fix the name_to_initials function in app.py to correctly detect pre-formatted initials."""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = []
for line in lines:
    # Find the buggy regex condition line and replace it
    if "_re.match(r'^[A-Za-z](" in line and "len(raw) <= 8" in line:
        # Replace with the corrected version that requires a dot to be present
        indent = '    '
        fixed.append(indent + "# Already looks like initials: has at least one dot (e.g. 'A.O.' or 'K.A.M.')\r\n")
        fixed.append(indent + "if '.' in raw and _re.match(r'^[A-Za-z](\\.[A-Za-z])*\\.?$', raw):\r\n")
        print(f"PATCHED line: {repr(line.rstrip())} -> initials-dot check")
    elif "# If it already looks like initials (only letters and dots, 5 chars or fewer)" in line:
        # skip this old comment
        pass
    elif "# Normalise: ensure dots between letters" in line:
        # skip old comment
        pass
    else:
        fixed.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed)

print("Done.")
