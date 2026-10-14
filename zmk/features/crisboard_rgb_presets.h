// SPDX-License-Identifier: MIT
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define CRISBOARD_RGB_APPLY_CMD 128
#define CRISBOARD_PRESET_COUNT 5
#define CRISBOARD_PRESET_HOLD_MS 2000

// Stable settings/wire format: hue 9, saturation 7, brightness 7,
// speed 3, effect 3, enabled 1. The two high bits remain reserved.
static inline uint32_t crisboard_rgb_pack(uint16_t h, uint8_t s, uint8_t b,
                                         uint8_t speed, uint8_t effect, bool on) {
    return h | ((uint32_t)s << 9) | ((uint32_t)b << 16) | ((uint32_t)speed << 23) |
           ((uint32_t)effect << 26) | ((uint32_t)on << 29);
}

static inline bool crisboard_rgb_valid(uint32_t value, uint8_t effect_count) {
    return (value >> 30) == 0 && (value & 511) <= 360 &&
           ((value >> 9) & 127) <= 100 && ((value >> 16) & 127) <= 100 &&
           ((value >> 23) & 7) >= 1 && ((value >> 23) & 7) <= 5 &&
           ((value >> 26) & 7) < effect_count;
}

static inline uint8_t crisboard_preset_crc(const uint8_t *data, uint8_t length) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            crc = (crc & 128) ? (uint8_t)((crc << 1) ^ 7) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

static inline void crisboard_preset_encode(uint8_t slot, uint32_t value, uint8_t data[8]) {
    data[0] = 0xcb;
    data[1] = 1;
    data[2] = slot;
    for (uint8_t i = 0; i < 4; i++) {
        data[i + 3] = (uint8_t)(value >> (8 * i));
    }
    data[7] = crisboard_preset_crc(data, 7);
}

static inline bool crisboard_preset_decode(uint8_t slot, const uint8_t data[8],
                                           uint8_t effect_count, uint32_t *value) {
    if (slot >= CRISBOARD_PRESET_COUNT || data[0] != 0xcb || data[1] != 1 ||
        data[2] != slot || data[7] != crisboard_preset_crc(data, 7)) {
        return false;
    }
    uint32_t packed = 0;
    for (uint8_t i = 0; i < 4; i++) {
        packed |= (uint32_t)data[i + 3] << (8 * i);
    }
    if (!crisboard_rgb_valid(packed, effect_count)) {
        return false;
    }
    *value = packed;
    return true;
}
