"""Sort compiler-generated unordered device dependency/support sets.

Zephyr 3 gen_handles.py emits these sets in process-dependent order. Preserve
all values and separators; then relink only the generated final-pass object.
No source file or device-tree property is modified.
"""
from pathlib import Path
from collections import Counter
import re
import subprocess
import sys

build = Path(sys.argv[1])
path = build / 'zephyr/dev_handles.c'
original = path.read_text()
pattern = re.compile(r'(__devicehdl_\w+\[\]\s*=\s*\{\s*)([^}]+)(\s*\};)')
seen = 0
def normalize(match):
    global seen
    seen += 1
    values = [value.strip() for value in match[2].split(',')]
    result, group = [], []
    for value in values:
        if value.isdigit() and 0 < int(value) < 32767:
            group.append(value)
        else:
            result.extend(sorted(group,key=int))
            group = []
            result.append(value)
    result.extend(sorted(group,key=int))
    assert Counter(values) == Counter(result)
    assert [v for v in values if not v.isdigit()] == [v for v in result if not v.isdigit()]
    return match[1] + ', '.join(result) + match[3]
normalized = pattern.sub(normalize,original)
assert seen > 0, 'No generated dependency lists found'
if normalized != original:
    path.write_text(normalized)
    subprocess.run(['west','build','-d',str(build)],check=True)
print(f'PASS: {seen} generated dependency/support lists retain all values and use deterministic order.')
