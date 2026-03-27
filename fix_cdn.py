import os, re

templates_dir = 'templates'

fixes = [
    'print_session.html',
    'print_report.html',
    'print_referral.html',
    'print_dass21.html',
    'print_case_note.html',
    'print_case.html',
    'student_profile.html',
    'dashboard.html',
]

for fname in fixes:
    path = os.path.join(templates_dir, fname)
    if not os.path.exists(path):
        print(f'SKIP: {fname}')
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all Google Fonts CDN URLs
    content = re.sub(r'https://fonts\.googleapis\.com/css2\?[^"\']+', '/static/css/inter.css', content)

    # Replace Flaticon CDN image
    content = content.replace(
        'https://cdn-icons-png.flaticon.com/512/7486/7486744.png',
        '/static/icon.png'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed: {fname}')

print('All done!')
