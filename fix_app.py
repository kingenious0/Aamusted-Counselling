import os

path = 'app.py'
if not os.path.exists(path):
    print(f'Error: {path} not found')
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "'SELECT id, name, programme FROM Student ORDER BY name').fetchall()"
replacement = "'SELECT id, name, case_number, programme FROM Student ORDER BY name').fetchall()"

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Successfully replaced all occurrences of target.')
else:
    print('Target string not found in app.py.')
