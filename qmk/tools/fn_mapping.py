"""Apply the fourteen owner-requested Fn changes to the verified original map.

SPDX-License-Identifier: GPL-2.0-or-later
"""

import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

# Matrix row/column, original symbol/value, requested symbol/value.
# Values belong to the pinned QMK 0.18.0 revision, not current QMK.
CHANGES = (
    (1, 0, "KC_CAPS", 0x39, "RGB_VAD", 0x5CCB),
    (1, 1, "KC_Q", 0x14, "RGB_VAI", 0x5CCA),
    (2, 0, "KC_TAB", 0x2B, "RGB_MODE_FORWARD", 0x5CC4),
    (2, 1, "KC_A", 0x04, "RGB_HUI", 0x5CC6),
    (3, 0, "KC_LSFT", 0xE1, "RGB_SAD", 0x5CC9),
    (3, 1, "KC_NONUS_BACKSLASH", 0x64, "RGB_SAI", 0x5CC8),
    (8, 1, "RGB_MODE_FORWARD", 0x5CC4, "KC_VOLU", 0xA9),
    (9, 1, "RGB_SAI", 0x5CC8, "KC_VOLD", 0xAA),
    (9, 0, "RGB_HUI", 0x5CC6, "KC_MNXT", 0xAB),
    (9, 2, "RGB_VAI", 0x5CCA, "KC_MPRV", 0xAC),
    (9, 5, "KC_SPC", 0x2C, "KC_MPLY", 0xAE),
    (8, 6, "KC_ENT", 0x28, "KC_MUTE", 0xA8),
    (6, 4, "KC_MUTE", 0xA8, "KC_TRNS", 0x01),
    (6, 3, "KC_MPLY", 0xAE, "KC_TRNS", 0x01),
)


def physical_index(row, col):
    side, local_row = divmod(row, 5)
    width = 6 if local_row == 0 else 7
    row_start = 0 if local_row == 0 else 12 + (local_row - 1) * 14
    return row_start + (col if side == 0 else width + width - 1 - col)


def apply_source(original):
    block = re.search(rb"\[_LOWER\]\s*=\s*LAYOUT\((.*?)\r?\n\)", original, re.S)
    if not block:
        raise ValueError("Expected the original LOWER layout")
    tokens = list(re.finditer(rb"[A-Z][A-Z0-9_]*(?:\([^)]*\))?", block[1]))
    if len(tokens) != 68:
        raise ValueError("Expected exactly 68 physical Fn keys")
    replacements = []
    for row, col, old, _, new, _ in CHANGES:
        token = tokens[physical_index(row, col)]
        if token[0].decode("ascii") != old:
            raise ValueError(f"Unexpected original Fn key at {row},{col}")
        replacements.append((block.start(1) + token.start(), block.start(1) + token.end(), new.encode("ascii")))
    result = original
    for start, end, value in sorted(replacements, reverse=True):
        result = result[:start] + value + result[end:]
    return result


def expected_map(recovered):
    layers = copy.deepcopy(recovered["layers"])
    lower = layers[2]
    for row, col, old, old_value, new, value in CHANGES:
        position = row * 7 + col
        if lower["raw_u16"][position] != old_value or lower["matrix"][row][col] != old:
            raise ValueError(f"Unexpected recovered Fn key at {row},{col}")
        lower["raw_u16"][position] = value
        lower["matrix"][row][col] = new
        side, local_row = divmod(row, 5)
        width = 6 if local_row == 0 else 7
        lower["physical_rows"][local_row]["right" if side else "left"][width - 1 - col if side else col] = new
    table = b"".join(struct.pack("<70H", *layer["raw_u16"]) for layer in layers)
    return {"original_keymap_sha256": recovered["keymap_sha256"],
            "requested_fn_changes": len(CHANGES),
            "keymap_sha256": hashlib.sha256(table).hexdigest(), "layers": layers}


if __name__ == "__main__":
    qmk = Path(__file__).resolve().parents[1]
    recovered = json.loads((qmk / "recovered/keymap.json").read_text(encoding="utf-8"))
    Path(sys.argv[1]).write_text(json.dumps(expected_map(recovered), indent=2) + "\n", encoding="utf-8")
