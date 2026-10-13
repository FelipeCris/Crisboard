"""Compile the actual current and historical indicator callbacks in native CI.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from pathlib import Path
import sys

qmk = Path(__file__).resolve().parents[1]
current = (qmk / 'keyboards/crisboard/keymaps/default/keymap.c').read_text(encoding='utf-8')
original = (qmk / 'snapshots/2023-06/crisboard/keymaps/default/keymap.c').read_text(encoding='utf-8')
helper = 'void set_color_split('
callback = 'void rgb_matrix_indicators_user('
assert current.count(helper) == original.count(callback) == 1
actual = current[current.index(helper):]
baseline = original[original.index(callback):].replace(callback, 'void original_rgb_matrix_indicators_user(', 1)
Path(sys.argv[1]).write_text(actual + '\n' + baseline,encoding='utf-8')
