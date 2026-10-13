// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include "quantum.h"

enum crisboard_preset_keycodes {
    CB_RGB_PRESET_1 = SAFE_RANGE + 2,
    CB_RGB_PRESET_2,
    CB_RGB_PRESET_3,
};

#define CB_RGB_PRESET_COUNT 3
#define CB_RGB_PRESET_EEPROM_BASE 64
#define CB_RGB_PRESET_HOLD_MS 2000

bool crisboard_process_rgb_presets(uint16_t keycode, keyrecord_t *record);
void crisboard_rgb_presets_scan(void);
