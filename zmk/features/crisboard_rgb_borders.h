// SPDX-License-Identifier: MIT
#pragma once
#include <stdbool.h>
#include <stdint.h>

// QMK ranges, local to either 34-LED half; not matrix/keymap positions.
static inline bool crisboard_rgb_is_border(uint8_t led) {
    return led <= 6 || (led >= 17 && led <= 20) || (led >= 23 && led <= 24) ||
           (led >= 27 && led <= 28) || (led >= 32 && led <= 33);
}
