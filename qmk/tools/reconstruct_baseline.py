"""Reproduce the two original applications before testing any optimization.

This is build recovery, not a new OLED or matrix feature. The complete baseline
application must match the original dump SHA256 before optimized builds proceed.
SPDX-License-Identifier: GPL-2.0-or-later
"""

import argparse
import hashlib
from pathlib import Path

from verify_usb_build import read_hex

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--keyboard-root", type=Path)
parser.add_argument("--baseline-hex", type=Path)
parser.add_argument("--side", choices=("left", "right"))
args = parser.parse_args()

if args.keyboard_root and args.side == "left":
    path = args.keyboard_root / "keymaps/default/keymap.c"
    source = path.read_bytes()
    block = b"""    /* this fixes the screen on and off bug */
    if (current_wpm > 0) {
        oled_on();
        anim_sleep = timer_read32();
    } else if (timer_elapsed32(anim_sleep) > OLED_TIMEOUT) {
        oled_off();
    }
"""
    if source.count(block) != 1:
        raise ValueError("June 2023 OLED block changed")
    path.write_bytes(source.replace(block, b""))
    print("Recovered left baseline: WPM OLED sleep block absent in original left dump.")

if args.baseline_hex:
    memory = read_hex(args.baseline_hex)
    image = bytes(memory.get(i, 255) for i in range(0x7000))
    expected = {
        "left": "01f934c4a40a9653e146a1cb1c0652e5a50bdb072af15a3f960c276f8daee1e5",
        "right": "a9d131153a88eada4022603b994662ae9a67eafd35e4bf1d4b0ce5ac990e7abb",
    }[args.side]
    actual = hashlib.sha256(image).hexdigest()
    if actual != expected:
        raise ValueError(f"Full {args.side} baseline differs from original: {actual}")
    print(f"PASS: entire {args.side} application matches original dump SHA256.")
