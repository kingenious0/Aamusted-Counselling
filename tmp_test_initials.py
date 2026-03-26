"""Test the name_to_initials function after patch."""
import re as _re

def name_to_initials(name_input):
    if not name_input:
        return ''
    raw = name_input.strip()
    # Already looks like initials: has at least one dot (e.g. 'A.O.' or 'K.A.M.')
    if '.' in raw and _re.match(r'^[A-Za-z](\.[A-Za-z])*\.?$', raw):
        letters = [c.upper() for c in raw if c.isalpha()]
        return '.'.join(letters) + '.'
    # Otherwise build initials from space-separated words
    parts = [p.strip() for p in raw.split() if p.strip()]
    letters = [p[0].upper() for p in parts if p and p[0].isalpha()]
    if not letters:
        return raw[:4].upper()
    return '.'.join(letters) + '.'

tests = [
    ('Ama Osei', 'A.O.'),
    ('A.O.', 'A.O.'),
    ('K.A.M.', 'K.A.M.'),
    ('John', 'J.'),
    ('Kwame Asante Mensah', 'K.A.M.'),
    ('kofi boateng', 'K.B.'),
    ('', ''),
]

all_ok = True
for inp, expected in tests:
    result = name_to_initials(inp)
    ok = result == expected
    if not ok:
        all_ok = False
    print(f"  [{'OK' if ok else 'FAIL'}] {inp!r:30s} -> {result!r}  (expected {expected!r})")

print()
print('ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED')
