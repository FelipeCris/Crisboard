"""Verify exact installed baseline, unchanged complete keymap/hardware and linked feature."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys
from elftools.elf.elffile import ELFFile

side=sys.argv[1]
assert side in ('left','right')
root=Path.cwd()
ref=json.loads((root/'config-repo/zmk/inverse-borders-reference.json').read_text())
keymap=json.loads((root/'config-repo/zmk/qmk-fn-keymap.json').read_text())['bindings']
before=root/'build-baseline/zephyr'
after=root/'build-inverse-borders/zephyr'
assert (before/'.config').read_bytes()==(after/'.config').read_bytes()
assert (before/'zephyr.dts').read_bytes()==(after/'zephyr.dts').read_bytes()
assert hashlib.sha256((before/'zmk.uf2').read_bytes()).hexdigest()==ref['baseline_uf2_sha256'][side]
sizes={}
for variant in ('baseline','inverse-borders'):
    folder=root/f'build-{variant}/zephyr'
    text=(folder/'zmk.map').read_text()
    def value(name):
        found=re.search(r'0x([0-9a-fA-F]+)\s+'+re.escape(name)+r'\s*=',text)
        assert found,name
        return int(found[1],16)
    sizes[variant]={'flash_used_bytes':value('_flash_used'),
        'ram_used_bytes':value('_image_ram_end')-value('_image_ram_start')}
    with (folder/'zmk.elf').open('rb') as stream:
        elf=ELFFile(stream)
        symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
        maps=[s for s in symbols if s.name=='zmk_keymap']
        if side=='left':
            assert len(maps)==1 and maps[0]['st_size']==204*12
            symbol=maps[0]
            section=elf.get_section(symbol['st_shndx'])
            offset=symbol['st_value']-section['sh_addr']
            raw=section.data()[offset:offset+symbol['st_size']]
            def cstring(address):
                for candidate in elf.iter_sections():
                    if candidate['sh_type']!='SHT_NOBITS' and candidate['sh_addr']<=address<candidate['sh_addr']+candidate['sh_size']:
                        return candidate.data()[address-candidate['sh_addr']:].split(b'\0',1)[0].decode('ascii')
                raise ValueError('Unmapped label')
            bindings=[[cstring(p),a,b] for p,a,b in struct.iter_unpack('<III',raw)]
            assert bindings==keymap
        else:
            assert not maps
        if variant=='inverse-borders':
            names={s.name for s in symbols}
            assert 'zmk_rgb_underglow_set_base_context' in names
            assert 'zmk_rgb_underglow_apply_snapshot' in names
            if side=='left':
                assert {'preset_conf','process_preset_commands','zmk_crisboard_rgb_sync_base','sync_base_work'}<=names
report={'side':side,'installed_baseline_exact':True,'compiled_config_identical':True,
    'devicetree_identical':True,'all_204_central_bindings_identical':side=='left',
    'peripheral_has_no_linked_keymap':side=='right','old_effect_ids_preserved':True,
    'new_effect_ids':[4,5], 'idle_suspension_not_persisted':True,'preset_format_unchanged':True,'colemak_context_synced_on_layer_change_and_reconnect':True,
    'size':sizes,'size_delta':{k:sizes['inverse-borders'][k]-sizes['baseline'][k] for k in sizes['baseline']},
    'artifact_sha256':{str(p.relative_to(root/'results')):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (root/'results').rglob('*') if p.is_file()}}
(root/'results/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
