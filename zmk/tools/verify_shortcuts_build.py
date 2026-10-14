"""Check the actual linked keymap and preserve hardware and compiled options."""
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
reference = json.loads((root / 'config-repo/zmk/shortcuts-keymap.json').read_text())


def without_keymap(text):
    match = re.search(r'\n\s*keymap\s*\{', text)
    assert match
    opening = text.index('{', match.start())
    depth = 1
    closing = opening + 1
    while depth:
        depth += (text[closing] == '{') - (text[closing] == '}')
        closing += 1
    assert text[closing] == ';'
    return text[:match.start()] + text[closing + 1:]


before_dir = root / 'build-baseline/zephyr'
after_dir = root / 'build-shortcuts/zephyr'
before_config = (before_dir / '.config').read_bytes()
after_config = (after_dir / '.config').read_bytes()
assert before_config == after_config, 'Compiled options changed'
assert b'CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_VOLTAGE=y' in after_config
assert b'CONFIG_ZMK_SETTINGS_RESET_ON_START=y' not in after_config
before_tree = without_keymap((before_dir / 'zephyr.dts').read_text())
after_tree = without_keymap((after_dir / 'zephyr.dts').read_text())
tree_diff = ''.join(difflib.unified_diff(before_tree.splitlines(True), after_tree.splitlines(True), fromfile='baseline', tofile='shortcuts'))
(root / 'results/generated-phandle-ids.diff').write_text(tree_diff)
# Zephyr assigns phandle IDs by first reference, including references in keymap.
# Its exported DTS retains symbolic references (&label), so removing only the
# generated per-node IDs preserves all relationship/property checks.
def without_generated_ids(text):
    return re.sub(r'\n\s*phandle = < 0x[0-9a-f]+ >;', '', text)

if without_generated_ids(before_tree) != without_generated_ids(after_tree):
    print(tree_diff)
    raise AssertionError('Hardware or behavior definitions changed beyond generated phandle IDs')
sizes, linked = {}, {}
for variant in ('baseline', 'shortcuts'):
    with (root / f'build-{variant}/zephyr/zmk.elf').open('rb') as stream:
        elf = ELFFile(stream)
        sizes[variant] = {
            'allocated_flash_bytes': sum(segment['p_filesz'] for segment in elf.iter_segments() if segment['p_type'] == 'PT_LOAD'),
            'allocated_ram_bytes': sum(section['sh_size'] for section in elf.iter_sections() if section['sh_flags'] & 2 and 0x20000000 <= section['sh_addr'] < 0x30000000),
        }
        matches = [symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols() if symbol.name == 'zmk_keymap']
        if not matches:
            assert side == 'right'
            linked[variant] = 'peripheral: keymap not linked; hardware and source verified'
            continue
        assert len(matches) == 1 and matches[0]['st_size'] == 204 * 12
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
        expected = reference['baseline_bindings' if variant == 'baseline' else 'bindings']
        assert bindings == expected, f'{variant}: unexpected linked keymap'
        linked[variant] = 'all 204 linked bindings match the verified reference'
        if variant == 'shortcuts':
            # Fn has the highest layer index and the same physical position in both bases.
            assert bindings[55] == bindings[68 + 55] == ['MO', 2, 0]
            for index, expected_binding in reference['fn_changes'].items():
                assert bindings[136 + int(index)] == expected_binding

baseline_hash = hashlib.sha256((before_dir / 'zmk.uf2').read_bytes()).hexdigest()
installed_hashes = {'left': '06e0eb55284c9f45f21526b90c6163de335c3f596a055fc73068f3f3dcf23d22',
                    'right': '703336391bd6215a804319a5ea15c2cddc3a7a8bc457341d6e517f2aee968e37'}
assert baseline_hash == installed_hashes[side], 'Baseline does not reproduce the installed voltage application'
report = {
    'side': side, 'compiled_config_identical': True,
    'hardware_and_behavior_devicetree_equivalent': True,
    'only_ignored_tree_metadata': 'generated per-node phandle IDs; all symbolic references and other properties checked',
    'installed_voltage_baseline_exact': True,
    'linked_keymap': linked, 'size': sizes,
    'size_delta': {key: sizes['shortcuts'][key] - sizes['baseline'][key] for key in sizes['baseline']},
    'artifact_sha256': {str(path.relative_to(root / 'results')): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in (root / 'results').rglob('*') if path.is_file()},
}
(root / 'results/verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
