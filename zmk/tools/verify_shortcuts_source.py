"""Limit this stage to the agreed wireless shortcuts and base/Fn selection."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo = Path(__file__).resolve().parents[2]
reference = json.loads((repo / 'zmk/shortcuts-keymap.json').read_text())
base = reference['baseline_commit']
keymap = 'config/boards/shields/Crisboard/crisboard.keymap'


def original(path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{base}:{path}']).replace(b'\r\n', b'\n')


def parse(text):
    return [re.findall(r'&\w+(?:\s+[A-Z_0-9]+)*', block)
            for block in re.findall(r'bindings\s*=\s*<([^>]+)>', text)]


old_layers = parse(original(keymap).decode())
new_source = (repo / keymap).read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(new_source).hexdigest() == reference['source_sha256']
new_layers = parse(new_source.decode())
assert [len(layer) for layer in new_layers] == [68, 68, 68]
token_values = {}
for token, value in zip(sum(old_layers, []), reference['baseline_bindings']):
    if token in token_values:
        assert token_values[token] == value
    token_values[token] = value
token_values.update({'&mo LOWER': ['MO', 2, 0],
                     '&to QWERTY': ['TO_LAYER', 1, 0],
                     '&to COLEMAK': ['TO_LAYER', 0, 0],
                     '&out OUT_TOG': ['OUTPUTS', 0, 0]})
actual = [token_values[token] for token in sum(new_layers, [])]
assert actual == reference['bindings'], 'Unexpected binding outside the agreed change'

# Assert the complete baseline-relative change, not just selected shortcuts.
expected = reference['baseline_bindings']
colemak = [row[:] for row in expected[:68]]
qwerty = [row[:] for row in expected[136:]]
fn = [row[:] for row in expected[68:136]]
colemak[55] = ['MO', 2, 0]
qwerty[55], qwerty[56] = ['MO', 2, 0], ['KEY_PRESS', 458979, 0]
agreed_fn = {
    13: ['TRANS', 0, 0], 14: ['BLUETOOTH', 3, 0],
    15: ['BLUETOOTH', 3, 1], 16: ['BLUETOOTH', 3, 2],
    17: ['BLUETOOTH', 0, 0], 18: ['TO_LAYER', 1, 0],
    19: ['TO_LAYER', 0, 0], 27: ['TRANS', 0, 0],
    28: ['TRANS', 0, 0], 29: ['TRANS', 0, 0], 30: ['TRANS', 0, 0],
    31: ['OUTPUTS', 0, 0], 55: ['MO', 2, 0],
}
assert reference['fn_changes'] == {str(i): value for i, value in agreed_fn.items()}
for index, value in agreed_fn.items():
    fn[index] = value
assert actual == colemak + qwerty + fn
assert actual[55] == actual[68 + 55] == ['MO', 2, 0]
assert all(actual[136 + i] == value for i, value in agreed_fn.items())
assert all(actual[i] == expected[i] for i in range(68) if i != 55)
assert all(actual[68 + i] == expected[136 + i] for i in range(68) if i not in (55, 56))

# Preserve every hardware/configuration file, including power, voltage and bonds.
paths = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', base, 'config']).decode().splitlines()
for path in paths:
    if path != keymap:
        assert original(path) == (repo / path).read_bytes().replace(b'\r\n', b'\n'), path
patches = ['battery-percentage.patch', 'battery-voltage.patch']
for patch in patches:
    path = f'zmk/patches/{patch}'
    assert original(path) == (repo / path).read_bytes().replace(b'\r\n', b'\n'), path
print('PASS: 204 bindings; Fn above both bases; five agreed wireless controls; all other config/display sources unchanged.')
