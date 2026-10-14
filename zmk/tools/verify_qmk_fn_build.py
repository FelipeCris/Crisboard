"""Validate complete linked maps, stable hardware/options and exact installed baselines."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import struct
import sys
from elftools.elf.elffile import ELFFile

side = sys.argv[1]
assert side in ('left', 'right')
root = Path.cwd()
reference = json.loads((root / 'config-repo/zmk/qmk-fn-keymap.json').read_text())


def remove_node(text, pattern, expected_properties=None):
    match = re.search(pattern, text)
    assert match, pattern
    opening = text.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    assert text[end] == ';'
    if expected_properties:
        node = text[opening + 1:end - 1]
        node = re.sub(r'\s*phandle = < 0x[0-9a-f]+ >;', '', node)
        properties = [re.sub(r'\s+', ' ', part.strip()) for part in node.split(';') if part.strip()]
        assert properties == expected_properties, properties
    return text[:match.start()] + text[end + 1:]


def hardware(text, target):
    text = remove_node(text, r'\n\s*keymap\s*\{')
    if target:
        text = remove_node(text, r'\n\s*(?:cb_preset:\s*)?crisboard_rgb_preset\s*\{')
        text = remove_node(text, r'\n\s*none:\s*behavior_none\s*\{',
            ['compatible = "zmk,behavior-none"', 'label = "NONE"', '#binding-cells = < 0x0 >'])
    else:
        text = remove_node(text, r'\n\s*trans:\s*behavior_transparent\s*\{',
            ['compatible = "zmk,behavior-transparent"', 'label = "TRANS"', '#binding-cells = < 0x0 >'])
    text = re.sub(r'\n\s*phandle = < 0x[0-9a-f]+ >;', '', text)
    return '\n'.join(line for line in text.splitlines() if line.strip())


before = root / 'build-baseline/zephyr'
after = root / 'build-qmk-fn/zephyr'
assert (before / '.config').read_bytes() == (after / '.config').read_bytes(), 'Compiled options changed'
before_tree = hardware((before / 'zephyr.dts').read_text(), False)
after_tree = hardware((after / 'zephyr.dts').read_text(), True)
if before_tree != after_tree:
    print('\n'.join(difflib.unified_diff(before_tree.splitlines(), after_tree.splitlines())))
    raise AssertionError('Hardware or native behavior definitions changed')
sizes, linked = {}, {}
for variant in ('baseline', 'qmk-fn'):
    folder = root / f'build-{variant}/zephyr'
    map_text = (folder / 'zmk.map').read_text()

    def symbol_value(name):
        match = re.search(r'0x([0-9a-fA-F]+)\s+' + re.escape(name) + r'\s*=', map_text)
        assert match, name
        return int(match[1], 16)

    sizes[variant] = {'flash_used_bytes': symbol_value('_flash_used'),
                      'ram_used_bytes': symbol_value('_image_ram_end') - symbol_value('_image_ram_start')}
    with (folder / 'zmk.elf').open('rb') as stream:
        elf = ELFFile(stream)
        symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
        matches = [symbol for symbol in symbols if symbol.name == 'zmk_keymap']
        if not matches:
            assert side == 'right'
            linked[variant] = 'peripheral: source/devicetree verified; no linked keymap'
        else:
            assert side == 'left' and len(matches) == 1 and matches[0]['st_size'] == 204 * 12
            symbol = matches[0]
            section = elf.get_section(symbol['st_shndx'])
            offset = symbol['st_value'] - section['sh_addr']
            raw = section.data()[offset:offset + symbol['st_size']]

            def cstring(address):
                for candidate in elf.iter_sections():
                    if candidate['sh_type'] != 'SHT_NOBITS' and candidate['sh_addr'] <= address < candidate['sh_addr'] + candidate['sh_size']:
                        return candidate.data()[address - candidate['sh_addr']:].split(b'\0', 1)[0].decode('ascii')
                raise ValueError('Unmapped behavior label')

            bindings = [[cstring(pointer), p1, p2] for pointer, p1, p2 in struct.iter_unpack('<III', raw)]
            assert bindings == reference['baseline_bindings' if variant == 'baseline' else 'bindings']
            linked[variant] = 'all 204 linked bindings match the verified map'
        if variant == 'qmk-fn':
            names = {symbol.name for symbol in symbols}
            assert 'zmk_rgb_underglow_apply_snapshot' in names
            if side == 'left':
                assert 'preset_conf' in names and 'process_preset_commands' in names
                rodata = b''.join(section.data() for section in elf.iter_sections() if section['sh_type'] == 'SHT_PROGBITS')
                for text in (b'crisboard_rgb', b'CLMK', b'QWRTY', b'Lower'):
                    assert text in rodata, text

installed = {'left': '0228fb6268c8f7b17a6d5e0874c5ae38118020509b115b9cf00fe0c7c7b488ac',
             'right': '703336391bd6215a804319a5ea15c2cddc3a7a8bc457341d6e517f2aee968e37'}
baseline_data = (before / 'zmk.uf2').read_bytes()
# The installed linker output contains one unordered two-handle set per side.
# Allow only that set's order to differ. Restoring its installed order must
# reproduce the entire original UF2 SHA, including every other payload/header.
permutation = {'left': ('__devicehdl_DT_N_S_soc_S_gpio_50000000', 0x5e0c4, [24, 10]),
               'right': ('__devicehdl_DT_N_S_kscan_0', 0x55e54, [2, 3])}[side]
name, address, original_handles = permutation
with (before / 'zmk.elf').open('rb') as stream:
    elf = ELFFile(stream)
    matches = [s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == name]
    assert len(matches) == 1
    assert matches[0]['st_value'] <= address and address + 4 <= matches[0]['st_value'] + matches[0]['st_size']
restored = bytearray(baseline_data)
found = False
for offset in range(0, len(restored), 512):
    magic1, magic2, flags, start, length = struct.unpack_from('<IIIII', restored, offset)
    assert (magic1, magic2) == (0x0a324655, 0x9e5d5157) and length == 256
    if start <= address and address + 4 <= start + length:
        assert not found
        found = True
        index = offset + 32 + address - start
        assert sorted(struct.unpack_from('<HH', restored, index)) == sorted(original_handles)
        struct.pack_into('<HH', restored, index, *original_handles)
assert found and hashlib.sha256(restored).hexdigest() == installed[side], 'Baseline changed beyond the proven handle permutation'
report = {'side': side, 'compiled_config_identical': True,
          'hardware_and_remaining_native_behaviors_equivalent': True,
          'expected_behavior_enablement_changes': ['TRANS unreferenced; NONE referenced for QMK KC_NO', 'CB_RGB_PRESET added'],
          'new_behavior': 'central RGB presets; global absolute RGB state applied to both halves',
          'installed_baseline_exact': hashlib.sha256(baseline_data).hexdigest() == installed[side],
          'installed_baseline_equivalent_after_handle_order': True,
          'baseline_handle_order': {'symbol': name, 'address': hex(address), 'bytes': 4,
                                    'installed_handles': original_handles,
                                    'restored_complete_uf2_sha256': installed[side]},
          'linked_keymap': linked,
          'size': sizes, 'size_delta': {key: sizes['qmk-fn'][key] - sizes['baseline'][key] for key in sizes['baseline']},
          'artifact_sha256': {str(path.relative_to(root / 'results')): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (root / 'results').rglob('*') if path.is_file()}}
(root / 'results/verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
