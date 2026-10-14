"""Check both compiled variants and the actual central binding table."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from elftools.elf.elffile import ELFFile

side = sys.argv[1]
assert side in ('left','right')
root = Path.cwd()
repo = root / 'config-repo'
reference = json.loads((repo / 'zmk/verified-keymap.json').read_text())
def config(path):
    return dict(line.split('=',1) for line in path.read_text().splitlines()
                if line.startswith('CONFIG_') and '=' in line)
before = config(root / 'build-icon/zephyr/.config')
after = config(root / 'build-percentage/zephyr/.config')
changes = {key:[before.get(key),after.get(key)] for key in before.keys() | after.keys()
           if before.get(key) != after.get(key)}
assert changes == {'CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_PERCENTAGE':[None,'y']}, changes
assert after['CONFIG_ZMK_WIDGET_BATTERY_STATUS'] == 'y'
assert after['CONFIG_ZMK_DISPLAY_STATUS_SCREEN_BUILT_IN'] == 'y'
assert after.get('CONFIG_ZMK_SETTINGS_RESET_ON_START') != 'y'
first_dts = (root / 'build-icon/zephyr/zephyr.dts').read_bytes()
second_dts = (root / 'build-percentage/zephyr/zephyr.dts').read_bytes()
assert first_dts == second_dts, 'Hardware/matrix/behavior definitions changed'
maps = {}
for variant in ('icon','percentage'):
    path = root / f'build-{variant}/zephyr/zmk.elf'
    assert path.exists()
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name('.symtab')
        matches = [s for s in symtab.iter_symbols() if s.name == 'zmk_keymap']
        if not matches:
            assert side == 'right', 'Central keymap is missing'
            maps[variant] = 'not linked on peripheral; unchanged devicetree verified'
            continue
        assert len(matches) == 1
        symbol = matches[0]
        assert symbol['st_size'] == 204*12
        section = elf.get_section(symbol['st_shndx'])
        offset = symbol['st_value'] - section['sh_addr']
        raw = section.data()[offset:offset+symbol['st_size']]
        def cstring(address):
            for candidate in elf.iter_sections():
                if candidate['sh_type'] == 'SHT_NOBITS':
                    continue
                if candidate['sh_addr'] <= address < candidate['sh_addr'] + candidate['sh_size']:
                    data = candidate.data()[address-candidate['sh_addr']:]
                    return data.split(b'\0',1)[0].decode('ascii')
            raise ValueError('Unmapped behavior label')
        actual = [[cstring(pointer),param1,param2] for pointer,param1,param2 in struct.iter_unpack('<III',raw)]
        assert actual == reference['bindings'], 'Installed 204-key map changed'
        maps[variant] = 'all 204 bindings match the installed map'
report = {'side':side, 'zmk_commit':'c7fdce863ac2f03bc70495f9904b127f2d99d85c',
    'zephyr_commit':'3861c95d11e95d35a63afca67c39e578e32ce81e',
    'percentage_backport_from':'58eb7a3305b11e465505e60657479346bec32f53',
    'only_compiled_config_change':changes, 'hardware_devicetree_identical':True, 'map_verification':maps,
    'artifact_sha256':{str(path.relative_to(root/'results')):hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (root/'results').rglob('*') if path.is_file()}}
(root / 'results/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
