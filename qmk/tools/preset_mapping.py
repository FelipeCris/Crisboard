"""Add only the five owner-selected Fn preset keys and their integration hooks.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from fn_mapping import apply_source as previous_source, expected_map as previous_map, physical_index

# QMK 0.18.0 without VIA: SAFE_RANGE = 0x5DB2; two existing custom codes.
PRESETS = (
    (6, 5, "KC_NO", 0, "CB_RGB_PRESET_1", 0x5DB4),
    (6, 4, "KC_TRNS", 1, "CB_RGB_PRESET_2", 0x5DB5),
    (6, 3, "KC_TRNS", 1, "CB_RGB_PRESET_3", 0x5DB6),
    (6, 2, "KC_O", 0x12, "CB_RGB_PRESET_4", 0x5DB7),
    (6, 1, "KC_P", 0x13, "CB_RGB_PRESET_5", 0x5DB8),
)
MODULE_FILES = {"keymaps/default/rgb_presets.c", "keymaps/default/rgb_presets.h"}
RULES_APPEND = b"\r\nSRC += keyboards/crisboard/keymaps/default/rgb_presets.c\r\n"

def apply_source(original):
    source = previous_source(original)
    block = re.search(rb"\[_LOWER\]\s*=\s*LAYOUT\((.*?)\r?\n\)", source, re.S)
    tokens = list(re.finditer(rb"[A-Z][A-Z0-9_]*(?:\([^)]*\))?", block[1]))
    replacements = []
    for row, col, old, _, new, _ in PRESETS:
        token = tokens[physical_index(row, col)]
        if token[0].decode("ascii") != old:
            raise ValueError("Unexpected existing Fn preset position")
        replacements.append((block.start(1)+token.start(),block.start(1)+token.end(),new.encode("ascii")))
    for start,end,value in sorted(replacements,reverse=True):
        source = source[:start]+value+source[end:]
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    source = source.replace(b"#include QMK_KEYBOARD_H", b'#include QMK_KEYBOARD_H'+newline+b'#include "rgb_presets.h"', 1)
    source = source.replace(b"bool process_record_user(uint16_t keycode, keyrecord_t *record) {",
        b"bool process_record_user(uint16_t keycode, keyrecord_t *record) {"+newline+
        b"    if (!crisboard_process_rgb_presets(keycode, record)) {"+newline+
        b"        return false;"+newline+b"    }", 1)
    marker = b"void set_color_split(uint8_t key_code, uint8_t r, uint8_t g, uint8_t b) {"
    source = source.replace(marker,b"void matrix_scan_user(void) {"+newline+
        b"    crisboard_rgb_presets_scan();"+newline+b"}"+newline+newline+marker,1)
    return source

def expected_map(recovered):
    result = previous_map(recovered)
    lower = result["layers"][2]
    for row,col,old,old_value,new,value in PRESETS:
        position=row*7+col
        if lower["raw_u16"][position] != old_value or lower["matrix"][row][col] != old:
            raise ValueError("Unexpected existing Fn map")
        lower["raw_u16"][position]=value
        lower["matrix"][row][col]=new
        lower["physical_rows"][row-5]["right"][6-col]=new
    table=b"".join(struct.pack("<70H",*layer["raw_u16"]) for layer in result["layers"])
    original=[v for layer in recovered["layers"] for v in layer["raw_u16"]]
    actual=[v for layer in result["layers"] for v in layer["raw_u16"]]
    result["requested_fn_changes"]=sum(a!=b for a,b in zip(original,actual))
    result["preset_keys_added"]=len(PRESETS)
    result["keymap_sha256"]=hashlib.sha256(table).hexdigest()
    return result

if __name__ == "__main__":
    qmk=Path(__file__).resolve().parents[1]
    recovered=json.loads((qmk/"recovered/keymap.json").read_text(encoding="utf-8"))
    Path(sys.argv[1]).write_text(json.dumps(expected_map(recovered),indent=2)+"\n",encoding="utf-8")
