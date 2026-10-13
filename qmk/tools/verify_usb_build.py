"""Check the complete compiled key table and Caterina application boundary.

SPDX-License-Identifier: GPL-2.0-or-later
"""

import hashlib
import json
from pathlib import Path
import struct
import sys


def read_hex(path):
    memory = {}
    base = 0
    ended = False
    for line in path.read_text(encoding="ascii").splitlines():
        if not line.startswith(":") or ended:
            raise ValueError("Invalid Intel HEX record")
        record = bytes.fromhex(line[1:])
        length, hi, lo, kind = record[:4]
        if len(record) != length + 5 or sum(record) & 255:
            raise ValueError("Invalid Intel HEX length/checksum")
        address = base + (hi << 8) + lo
        data = record[4:-1]
        if kind == 0:
            for offset, value in enumerate(data):
                location = address + offset
                if location in memory or location >= 0x7000:
                    raise ValueError("Overlap or write into Caterina bootloader")
                memory[location] = value
        elif kind == 1:
            ended = True
        elif kind == 2:
            base = int.from_bytes(data, "big") << 4
        elif kind == 4:
            base = int.from_bytes(data, "big") << 16
        elif kind not in (3, 5):
            raise ValueError("Unsupported Intel HEX record")
    if not ended or not memory or min(memory) != 0:
        raise ValueError("Incomplete application image")
    return memory


def verify(hex_path, symbols_path, recovered_path):
    memory = read_hex(hex_path)
    symbols = []
    for line in symbols_path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if len(fields) == 4 and (fields[3] == "keymaps" or fields[3].startswith("keymaps.lto_priv.")):
            symbols.append((int(fields[0], 16), int(fields[1], 16)))
    if len(symbols) != 1 or symbols[0][1] != 420:
        raise ValueError("Expected one 420-byte keymaps symbol")
    offset, size = symbols[0]
    actual = bytes(memory[offset + i] for i in range(size))
    recovered = json.loads(recovered_path.read_text(encoding="utf-8"))
    expected = b"".join(struct.pack("<70H", *layer["raw_u16"]) for layer in recovered["layers"])
    if actual != expected:
        raise ValueError("Compiled table differs from the expected complete map")
    return {
        "hex_sha256": hashlib.sha256(hex_path.read_bytes()).hexdigest(),
        "application_end": max(memory) + 1,
        "caterina_application_limit": 0x7000,
        "free_application_bytes": 0x7000 - max(memory) - 1,
        "keymap_offset": offset,
        "keymap_sha256": hashlib.sha256(actual).hexdigest(),
        "expected_keymap_matches": True,
        "requested_fn_changes": recovered.get("requested_fn_changes", 0),
    }


if __name__ == "__main__":
    print(json.dumps(verify(*(Path(arg) for arg in sys.argv[1:])), indent=2))
