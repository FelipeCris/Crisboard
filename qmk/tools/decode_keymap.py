"""Decode only the two verified Crisboard USB dumps from October 2026.

No hardware access. The offsets and legacy keycode values are specific to these
images, not to arbitrary QMK firmware. Python 3 standard library only.
SPDX-License-Identifier: GPL-2.0-or-later
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct


KNOWN_DUMPS = {
    "069eae24b773643071d7ad368c4b63536e603040775edea4b1e86a19c22b935d": "izquierda",
    "32347d004cb6d5b779809a92848d4117994e7b0a412bd19088aaed46d8d6c90f": "derecha",
}
OFFSET = 0x047E
SIZE = 420
LAYERS = ("COLEMAK", "QWERTY", "LOWER")
CODES = {4 + i: f"KC_{chr(65 + i)}" for i in range(26)}
CODES.update({0x1D + i: f"KC_{i}" for i in range(1, 10)})
CODES.update({0x39 + i: f"KC_F{i}" for i in range(1, 13)})
CODES.update({
    0: "KC_NO", 0x27: "KC_0", 0x28: "KC_ENT", 0x29: "KC_ESC",
    0x2A: "KC_BSPC", 0x2B: "KC_TAB", 0x2C: "KC_SPC", 0x2D: "KC_MINUS",
    0x2F: "KC_LBRC", 0x30: "KC_RBRC", 0x31: "KC_BSLS", 0x33: "KC_SCLN",
    0x34: "KC_QUOT", 0x35: "KC_GRV", 0x36: "KC_COMM", 0x37: "KC_DOT",
    0x38: "KC_SLSH", 0x39: "KC_CAPS", 0x46: "KC_PSCR", 0x4A: "KC_HOME",
    0x4C: "KC_DEL", 0x4D: "KC_END", 0x4F: "KC_RIGHT", 0x50: "KC_LEFT",
    0x51: "KC_DOWN", 0x52: "KC_UP", 0x64: "KC_NONUS_BACKSLASH",
    0xA8: "KC_MUTE", 0xAE: "KC_MPLY", 0xE0: "KC_LCTRL", 0xE1: "KC_LSFT",
    0xE2: "KC_LALT", 0xE3: "KC_LGUI", 0xE6: "KC_ALGR",
    0x5102: "MO(_LOWER)", 0x5200: "DF(_COLEMAK)", 0x5201: "DF(_QWERTY)",
    0x5CC3: "RGB_TOG", 0x5CC4: "RGB_MODE_FORWARD", 0x5CC6: "RGB_HUI",
    0x5CC8: "RGB_SAI", 0x5CCA: "RGB_VAI", 0x5CCC: "RGB_SPI", 0x5CCD: "RGB_SPD",
})


def decode(data):
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != 32768 or digest not in KNOWN_DUMPS:
        raise ValueError("La imagen no es uno de los dos respaldos verificados; no se aplican estos offsets.")
    table = data[OFFSET:OFFSET + SIZE]
    layers = []
    for index, name in enumerate(LAYERS):
        values = list(struct.unpack_from("<70H", table, index * 140))
        symbols = [CODES[v] for v in values]
        matrix = [symbols[i:i + 7] for i in range(0, 70, 7)]
        if matrix[0][6] != "KC_NO" or matrix[5][6] != "KC_NO":
            raise ValueError("Las dos posiciones sin switch no coinciden con crisboard.h.")
        physical = []
        for row in range(5):
            width = 6 if row == 0 else 7
            physical.append({
                "left": matrix[row][:width],
                "right": list(reversed(matrix[row + 5][:width])),
            })
        layers.append({"name": name, "index": index, "raw_u16": values,
                       "matrix": matrix, "physical_rows": physical})
    return {"firmware_sha256": digest, "side": KNOWN_DUMPS[digest],
            "offset": OFFSET, "byte_count": SIZE,
            "keymap_sha256": hashlib.sha256(table).hexdigest(), "layers": layers}


def render_c(result):
    lines = [
        "// SPDX-License-Identifier: GPL-2.0-or-later",
        "// Reconstructed keymap ONLY; not the complete installed firmware source.",
        "// Both verified USB halves contain this same 420-byte table.",
        "// Legacy QMK symbols: see ../README.md before attempting a build.",
        "#include QMK_KEYBOARD_H", "",
        "enum recovered_layers { _COLEMAK, _QWERTY, _LOWER };", "",
        "const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {",
    ]
    for layer in result["layers"]:
        lines.append(f"    [_{layer['name']}] = LAYOUT(")
        for i, row in enumerate(layer["physical_rows"]):
            comma = "," if i < 4 else ""
            lines.append("        " + ", ".join(row["left"]) + ",    "
                         + ", ".join(row["right"]) + comma)
        lines.append("    ),")
    lines.extend(["};", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--c-out", type=Path)
    args = parser.parse_args()
    result = decode(args.firmware.read_bytes())
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(serialized, encoding="utf-8")
    if args.c_out:
        args.c_out.parent.mkdir(parents=True, exist_ok=True)
        args.c_out.write_text(render_c(result), encoding="utf-8")
    if not args.json_out and not args.c_out:
        print(serialized, end="")
    else:
        print(f"{result['side']}: 3 capas, 68 switches, SHA256 del mapa {result['keymap_sha256']}")


if __name__ == "__main__":
    main()
