"""Verify the complete QMK map, agreed wireless overrides and unchanged hardware."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo = Path(__file__).resolve().parents[2]
ref = json.loads((repo / 'zmk/qmk-fn-keymap.json').read_text())
keymap = 'config/boards/shields/Crisboard/crisboard.keymap'
source = (repo / keymap).read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(source).hexdigest() == ref['source_sha256']
layers = [re.findall(r'&\w+(?:\s+[A-Z_0-9]+)*', raw)
          for raw in re.findall(r'bindings\s*=\s*<([^>]+)>', source.decode())]
assert layers == ref['source_bindings']
assert [len(layer) for layer in layers] == [68, 68, 68]
assert ref['wireless_overrides'] == {'14': '&bt BT_SEL 0', '15': '&bt BT_SEL 1',
    '16': '&bt BT_SEL 2', '17': '&bt BT_CLR', '31': '&out OUT_TOG'}
for index, value in ref['wireless_overrides'].items():
    assert layers[2][int(index)] == value
qmk = repo / 'qmk/keyboards/crisboard/keymaps/default/keymap.c'
qmk_source = qmk.read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(qmk_source).hexdigest() == ref['qmk_source_sha256']
blocks = dict(re.findall(r'\[(_\w+)\]\s*=\s*LAYOUT\((.*?)\n\)', qmk_source.decode(), re.S))
actual_qmk = [[entry.strip() for entry in blocks[name].split(',')]
              for name in ('_COLEMAK', '_QWERTY', '_LOWER')]
assert actual_qmk == ref['qmk_codes']
assert layers[0][55] == layers[1][55] == '&mo LOWER'
assert layers[0][56] == layers[1][56] == '&kp LWIN'
assert layers[2][20:25] == [f'&cb_preset {i}' for i in range(5)]
expected = {12: '&rgb_ug RGB_BRD', 13: '&rgb_ug RGB_BRI',
    26: '&rgb_ug RGB_EFF', 27: '&rgb_ug RGB_HUI', 40: '&rgb_ug RGB_SAD',
    41: '&rgb_ug RGB_SAI', 46: '&kp PRINTSCREEN', 47: '&kp C_MUTE',
    51: '&rgb_ug RGB_SPD', 52: '&kp C_VOLUME_UP', 53: '&rgb_ug RGB_SPI',
    62: '&kp C_PLAY_PAUSE', 65: '&kp C_PREVIOUS',
    66: '&kp C_VOLUME_DOWN', 67: '&kp C_NEXT'}
for index, token in expected.items():
    assert layers[2][index] == token
base = ref['baseline_commit']
paths = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', base, 'config']).decode().splitlines()
for path in paths:
    if path == keymap:
        continue
    original = subprocess.check_output(['git', '-C', str(repo), 'show', f'{base}:{path}']).replace(b'\r\n', b'\n')
    assert original == (repo / path).read_bytes().replace(b'\r\n', b'\n'), path
print('PASS: all 204 positions, five wireless overrides, five RGB presets, media/RGB keys and unchanged hardware config.')
