"""Sort Zephyr's unordered native handle sets before every generation pass.

Editing dev_handles.c alone is insufficient: relinking may regenerate it.
Only the order of the two emitted sets changes; injected dependencies retain
their native order, and no device, dependency, separator or handle is removed.
"""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / 'scripts/gen_handles.py'
text = path.read_text()
for field in ('__depends', '__supports'):
    old = f'hdls.extend(dn.__device.dev_handle for dn in sn.{field})'
    new = f'hdls.extend(sorted(dn.__device.dev_handle for dn in sn.{field}))'
    assert text.count(old) == 1, field
    text = text.replace(old, new)
path.write_text(text)
print('PASS: native generated dependency/support sets are sorted at their source.')
