"""Compare the installed percentage baseline and voltage variant."""
from pathlib import Path
import hashlib
import json
import struct
import sys
from elftools.elf.elffile import ELFFile

side = sys.argv[1]
assert side in ('left', 'right')
root = Path.cwd()
repo = root / 'config-repo'
reference = json.loads((repo / 'zmk/verified-keymap.json').read_text())
def config(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines()
                if line.startswith('CONFIG_') and '=' in line)
before = config(root / 'build-percentage/zephyr/.config')
after = config(root / 'build-voltage/zephyr/.config')
changes = {key: [before.get(key), after.get(key)] for key in before.keys() | after.keys()
           if before.get(key) != after.get(key)}
assert changes == {'CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_VOLTAGE': [None, 'y']}, changes
assert after['CONFIG_ZMK_WIDGET_BATTERY_STATUS'] == 'y'
assert after['CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_PERCENTAGE'] == 'y'
assert after['CONFIG_ZMK_BATTERY_REPORTING'] == 'y'
assert after['CONFIG_ZMK_BATTERY_REPORT_INTERVAL'] == before['CONFIG_ZMK_BATTERY_REPORT_INTERVAL']
assert after.get('CONFIG_ZMK_SETTINGS_RESET_ON_START') != 'y'
first = (root / 'build-percentage/zephyr/zephyr.dts').read_bytes()
second = (root / 'build-voltage/zephyr/zephyr.dts').read_bytes()
assert first == second, 'Hardware/matrix/behavior definitions changed'
maps, sizes = {}, {}
for variant in ('percentage', 'voltage'):
    with (root / f'build-{variant}/zephyr/zmk.elf').open('rb') as stream:
        elf = ELFFile(stream)
        sizes[variant] = {
            'allocated_flash_bytes': sum(segment['p_filesz'] for segment in elf.iter_segments()
                                         if segment['p_type'] == 'PT_LOAD'),
            'allocated_ram_bytes': sum(section['sh_size'] for section in elf.iter_sections()
                                       if section['sh_flags'] & 2 and 0x20000000 <= section['sh_addr'] < 0x30000000),
        }
        symbols = elf.get_section_by_name('.symtab')
        matches = [s for s in symbols.iter_symbols() if s.name == 'zmk_keymap']
        if not matches:
            assert side == 'right'
            maps[variant] = 'not linked on peripheral; unchanged devicetree verified'
            continue
        assert len(matches) == 1
        symbol = matches[0]
        assert symbol['st_size'] == 204 * 12
        section = elf.get_section(symbol['st_shndx'])
        offset = symbol['st_value'] - section['sh_addr']
        raw = section.data()[offset:offset + symbol['st_size']]
        def cstring(address):
            for candidate in elf.iter_sections():
                if candidate['sh_type'] != 'SHT_NOBITS' and candidate['sh_addr'] <= address < candidate['sh_addr'] + candidate['sh_size']:
                    return candidate.data()[address - candidate['sh_addr']:].split(b'\0', 1)[0].decode('ascii')
            raise ValueError('Unmapped behavior label')
        bindings = [[cstring(pointer), p1, p2] for pointer, p1, p2 in struct.iter_unpack('<III', raw)]
        assert bindings == reference['bindings'], 'Installed 204-key map changed'
        maps[variant] = 'all 204 bindings match the installed map'
report = {'side': side, 'only_compiled_config_change': changes,
          'hardware_devicetree_identical': True, 'map_verification': maps,
          'battery_report_interval_seconds': int(after['CONFIG_ZMK_BATTERY_REPORT_INTERVAL']),
          'size': sizes,
          'size_delta': {key: sizes['voltage'][key] - sizes['percentage'][key] for key in sizes['voltage']},
          'artifact_sha256': {str(path.relative_to(root / 'results')): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (root / 'results').rglob('*') if path.is_file()}}
(root / 'results/verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
