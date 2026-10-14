"""Reject keyboard changes beyond the explicit battery-widget options."""
from pathlib import Path
import hashlib
import json
import subprocess

repo = Path(__file__).resolve().parents[2]
expected = json.loads((repo / 'zmk/verified-keymap.json').read_text())
base = '5249218a64f71c5d4c69028b9ac4272358cb9837'
def original(path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{base}:{path}'])
keymap = 'config/boards/shields/Crisboard/crisboard.keymap'
assert hashlib.sha256((repo / keymap).read_bytes().replace(b'\r\n',b'\n')).hexdigest() == expected['source_sha256']
paths = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', base, 'config']).decode().splitlines()
for path in paths:
    before = original(path).replace(b'\r\n', b'\n')
    after = (repo / path).read_bytes().replace(b'\r\n', b'\n')
    if path.endswith(('crisboard_left.conf', 'crisboard_right.conf')):
        before = before.replace(b'# CONFIG_ZMK_WIDGET_BATTERY_STATUS=n',
            b'CONFIG_ZMK_WIDGET_BATTERY_STATUS=y\nCONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_PERCENTAGE=y\nCONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_VOLTAGE=y')
    elif path == 'config/west.yml':
        assert b'revision: main' not in after
        assert b'revision: c7fdce863ac2f03bc70495f9904b127f2d99d85c' in after
        assert b'revision: 3861c95d11e95d35a63afca67c39e578e32ce81e' in after
        continue
    assert before.rstrip(b'\n') == after.rstrip(b'\n'), path
print('PASS: every keyboard file preserved except the explicit battery display options per half.')
