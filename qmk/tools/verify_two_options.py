"""Require the size options, approved Fn map, and isolated preset integration.

SPDX-License-Identifier: GPL-2.0-or-later
"""

import hashlib
import json
from pathlib import Path

from uniform_mode import apply_source, MODULE_FILES, RULES_APPEND

qmk = Path(__file__).resolve().parents[1]
snapshot = qmk / "snapshots/2023-06/crisboard"
working = qmk / "keyboards/crisboard"
manifest = json.loads((snapshot.parent / "manifest.json").read_text(encoding="utf-8"))
expected_paths = set(manifest["source_files_sha256"])
for directory in (snapshot, working):
    paths = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    allowed = expected_paths if directory == snapshot else expected_paths | MODULE_FILES
    if paths != allowed:
        raise ValueError("Source inventory differs from the archived ten files")
for name, digest in manifest["source_files_sha256"].items():
    original = (snapshot / name).read_bytes()
    if hashlib.sha256(original).hexdigest() != digest:
        raise ValueError(f"Archived source changed: {name}")
    expected = original
    if name == "config.h":
        flag = b" #  define ENABLE_RGB_MATRIX_CYCLE_SPIRAL"
        if original.count(flag) != 1:
            raise ValueError("Expected one CYCLE_SPIRAL declaration")
        expected = original.replace(flag, b"//" + flag)
    elif name == "rules.mk":
        if b"LTO_ENABLE" in original:
            raise ValueError("Archive already declares LTO")
        expected += b"\r\n# Link-time optimization\r\nLTO_ENABLE = yes\r\n"
        expected += RULES_APPEND
    elif name == "keymaps/default/keymap.c":
        expected = apply_source(original)
    if (working / name).read_bytes() != expected:
        raise ValueError(f"Unexpected source change outside approved Fn/preset integration: {name}")
print("PASS: approved Fn/preset table plus Uniform only; Colemak/QWERTY, normal RGB indicators, brightness, OLED and puppy preserved.")
