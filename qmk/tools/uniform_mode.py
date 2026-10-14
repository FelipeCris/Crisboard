"""Add one selectable RGB mode without changing any existing key positions.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from preset_mapping import apply_source as preset_source, MODULE_FILES as PRESET_FILES, RULES_APPEND as PRESET_RULES

MODULE_FILES = PRESET_FILES | {"keymaps/default/rgb_matrix_user.inc"}
RULES_APPEND = PRESET_RULES + b"RGB_MATRIX_CUSTOM_USER = yes\r\n"

def apply_source(original):
    source = preset_source(original)
    marker = b"            hsv2 = rgb_matrix_get_hsv();"
    if source.count(marker) != 1:
        raise ValueError("Expected one Colemak border override")
    guard = (b"            // Uniform is a separate selectable mode; other modes keep their borders.\n"
             b"            if (rgb_matrix_get_mode() == RGB_MATRIX_CUSTOM_CRISBOARD_UNIFORM) {\n"
             b"                break;\n"
             b"            }\n\n")
    return source.replace(marker, guard + marker, 1)
