// SPDX-License-Identifier: GPL-2.0-or-later
#include "rgb_presets.h"
#include "eeconfig.h"
#include <avr/eeprom.h>
#include <string.h>

#if defined(VIA_ENABLE) || defined(DYNAMIC_KEYMAP_ENABLE)
#    error "Review preset EEPROM allocation before enabling dynamic keymaps"
#endif

// This layout is specific to the pinned QMK 0.18.0 revision, without VIA.
_Static_assert(SAFE_RANGE == 0x5DB2, "Review preset keycodes after changing QMK");

#define PRESET_MAGIC 0xCB51
#define PRESET_VERSION 1
#define PRESET_LAYER 2
#define NO_PRESET 0xFF

typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t version;
    uint8_t hue, saturation, value;
    uint8_t mode, speed, enabled;
    uint8_t crc;
} preset_t;

_Static_assert(sizeof(preset_t) == 10, "Preset EEPROM record size changed");
_Static_assert(CB_RGB_PRESET_EEPROM_BASE >= EECONFIG_SIZE, "Preset overlaps QMK settings");
_Static_assert(CB_RGB_PRESET_EEPROM_BASE + CB_RGB_PRESET_COUNT * sizeof(preset_t) <= E2END + 1, "Presets exceed EEPROM");

static uint8_t pending_slot = NO_PRESET;
static uint8_t pending_row, pending_col;
static uint16_t pending_started;
static bool pending_saved, pending_can_save;

static uint16_t preset_address(uint8_t slot) {
    return CB_RGB_PRESET_EEPROM_BASE + slot * sizeof(preset_t);
}

static uint8_t preset_crc(const preset_t *preset) {
    const uint8_t *bytes = (const uint8_t *)preset;
    uint8_t crc = 0;
    for (uint8_t i = 2; i < sizeof(*preset) - 1; ++i) {
        crc ^= bytes[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

static void preset_save(uint8_t slot) {
    // Read the RGB configuration, never LED pixels or the indicator HSV copies.
    HSV base = rgb_matrix_get_hsv();
    preset_t preset = {
        .magic = PRESET_MAGIC,
        .version = PRESET_VERSION,
        .hue = base.h,
        .saturation = base.s,
        .value = base.v,
        .mode = rgb_matrix_get_mode(),
        .speed = rgb_matrix_get_speed(),
        .enabled = rgb_matrix_is_enabled() != 0,
    };
    preset.crc = preset_crc(&preset);
    uint16_t address = preset_address(slot);
    preset_t previous;
    eeprom_read_block(&previous, (const void *)(uintptr_t)address, sizeof(previous));
    if (memcmp(&preset, &previous, sizeof(preset)) == 0) {
        return;
    }
    // Invalidate first and commit the signature last. Interrupted saves cannot
    // make a partial record valid. Other slots and native QMK settings stay put.
    eeprom_update_byte((uint8_t *)(uintptr_t)address, 0);
    eeprom_update_block((const uint8_t *)&preset + 2, (void *)(uintptr_t)(address + 2), sizeof(preset) - 2);
    eeprom_update_byte((uint8_t *)(uintptr_t)(address + 1), PRESET_MAGIC >> 8);
    eeprom_update_byte((uint8_t *)(uintptr_t)address, PRESET_MAGIC & 0xFF);
}

static void preset_load(uint8_t slot) {
    preset_t preset;
    eeprom_read_block(&preset, (const void *)(uintptr_t)preset_address(slot), sizeof(preset));
    if (preset.magic != PRESET_MAGIC || preset.version != PRESET_VERSION ||
        preset.crc != preset_crc(&preset) || preset.mode < 1 ||
        preset.mode >= RGB_MATRIX_EFFECT_MAX || preset.enabled > 1) {
        return;
    }
    // QMK 0.18 ignores mode/HSV changes while RGB is disabled. Enable before
    // applying and restore the saved on/off state after all parameters are set.
    rgb_matrix_enable();
    rgb_matrix_mode(preset.mode);
    rgb_matrix_sethsv(preset.hue, preset.saturation, preset.value);
    rgb_matrix_set_speed(preset.speed);
    if (!preset.enabled) {
        rgb_matrix_disable();
    }
    // Keep the selected configuration across a power cycle, like normal RGB
    // controls. Loading does not overwrite any of the preset records.
    eeconfig_update_rgb_matrix();
}

void crisboard_rgb_presets_scan(void) {
    if (pending_slot == NO_PRESET || pending_saved) {
        return;
    }
    if (!layer_state_is(PRESET_LAYER)) {
        pending_can_save = false;
    }
    if (pending_can_save && timer_elapsed(pending_started) >= CB_RGB_PRESET_HOLD_MS) {
        preset_save(pending_slot);
        pending_saved = true;
    }
}

bool crisboard_process_rgb_presets(uint16_t keycode, keyrecord_t *record) {
    // Match release by physical position even if Fn was released first.
    if (!record->event.pressed && pending_slot != NO_PRESET &&
        record->event.key.row == pending_row && record->event.key.col == pending_col) {
        if (!pending_saved) {
            if (pending_can_save && layer_state_is(PRESET_LAYER) &&
                timer_elapsed(pending_started) >= CB_RGB_PRESET_HOLD_MS) {
                preset_save(pending_slot);
            } else {
                preset_load(pending_slot);
            }
        }
        pending_slot = NO_PRESET;
        return false;
    }
    if (keycode < CB_RGB_PRESET_1 || keycode > CB_RGB_PRESET_5) {
        return true;
    }
    if (record->event.pressed && pending_slot == NO_PRESET && layer_state_is(PRESET_LAYER)) {
        pending_slot = keycode - CB_RGB_PRESET_1;
        pending_row = record->event.key.row;
        pending_col = record->event.key.col;
        pending_started = timer_read();
        pending_saved = false;
        pending_can_save = true;
    }
    return false;
}
