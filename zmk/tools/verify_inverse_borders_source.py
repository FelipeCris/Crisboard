"""Keep the validated map, hardware, settings format and legacy effect IDs unchanged."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

repo=Path(__file__).resolve().parents[2]
ref=json.loads((repo/'zmk/inverse-borders-reference.json').read_text())
base=ref['installed_source_commit']

def original(path):
    return subprocess.check_output(['git','-C',str(repo),'show',f'{base}:{path}']).replace(b'\r\n',b'\n')

paths=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',base,'config','qmk']).decode().splitlines()
for path in paths:
    assert original(path)==(repo/path).read_bytes().replace(b'\r\n',b'\n'),path
header='zmk/features/crisboard_rgb_presets.h'
expected=original(header).replace(b'#define CRISBOARD_RGB_APPLY_CMD 128\n',
    b'#define CRISBOARD_RGB_APPLY_CMD 128\n#define CRISBOARD_RGB_BASE_CMD 129\n#define CRISBOARD_RGB_EFFECT_COUNT 5\n')
assert expected==(repo/header).read_bytes().replace(b'\r\n',b'\n'), 'Preset wire/settings format changed'
driver='zmk/features/behavior_crisboard_rgb_preset.c'
expected=original(driver).replace(b'crisboard_preset_decode(slot, record, 4, &presets[slot])',
    b'crisboard_preset_decode(slot, record, CRISBOARD_RGB_EFFECT_COUNT, &presets[slot])')
assert expected==(repo/driver).read_bytes().replace(b'\r\n',b'\n'), 'Existing preset logic changed'
qmk=(repo/'qmk/keyboards/crisboard/keymaps/default/keymap.c').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(qmk).hexdigest()==ref['qmk_source_sha256']
ranges=[int(n.strip()) for n in re.search(rb'int ranges2\[\] = \{([^}]+)\}',qmk)[1].split(b',')]
assert ranges==ref['qmk_global_border_ranges']
leds=[i for start,end in zip(ranges[::2],ranges[1::2]) for i in range(start,end+1)]
assert [i for i in leds if i<34]==[i-34 for i in leds if i>=34]==ref['border_leds_per_half']
assert len(ref['border_leds_per_half'])==17
assert ref['old_effect_ids']=={'solid':0,'breathe':1,'spectrum':2,'swirl':3}
assert ref['new_effect_id']==4 and ref['hue_offset_degrees']==180 and ref['colemak_only']
print('PASS: full keymap/hardware unchanged, exact QMK borders, stable preset format and four legacy effect IDs.')
