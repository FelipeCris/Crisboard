// SPDX-License-Identifier: GPL-2.0-or-later
#include "quantum.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

#define MASTER_LEFT
enum { _COLEMAK, _QWERTY, _LOWER };
typedef struct { bool init; } effect_params_t;
static RGB leds[68];
static bool master;
static uint8_t mode;
static uint32_t layer_state, default_layer_state;
static const HSV base = {37, 201, 137};
static HSV hsv, hsv2;
static int coloroffset = 50, coloroffset2 = 127;
static unsigned solid_calls;
static effect_params_t *last_params;
static bool solid_result;

static bool is_keyboard_master(void) { return master; }
static uint8_t get_highest_layer(uint32_t state) {
    uint8_t highest = 0;
    while (state >>= 1) ++highest;
    return highest;
}
HSV rgb_matrix_get_hsv(void) { return base; }
uint8_t rgb_matrix_get_mode(void) { return mode; }
// Keep channels distinguishable; the same converter is used for old and new.
static RGB hsv_to_rgb(HSV color) { return (RGB){color.h, color.s, color.v}; }
static void rgb_matrix_set_color(int led, uint8_t r, uint8_t g, uint8_t b) {
    assert(led >= 0 && led < 68);
    leds[led] = (RGB){r,g,b};
}
static bool SOLID_COLOR(effect_params_t *params) {
    ++solid_calls;
    last_params = params;
    return solid_result;
}
#define RGB_MATRIX_EFFECT(name)
#define RGB_MATRIX_CUSTOM_EFFECT_IMPLS
#include "../keyboards/crisboard/keymaps/default/rgb_matrix_user.inc"
#undef RGB_MATRIX_CUSTOM_EFFECT_IMPLS
#undef RGB_MATRIX_EFFECT

// Generated verbatim from the working keymap and the archived callback.
// Keep the historical int/sizeof loop comparisons unchanged in both callbacks.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#include "crisboard_indicators_under_test.inc"
#pragma GCC diagnostic pop

static void render(void (*indicators)(void)) {
    for (unsigned i=0; i<68; ++i) {
        HSV background = base;
        if (mode != RGB_MATRIX_SOLID_COLOR && mode != RGB_MATRIX_CUSTOM_CRISBOARD_UNIFORM)
            background.h = (uint8_t)((base.h+i)%255);
        leds[i] = hsv_to_rgb(background);
    }
    for (unsigned side=0; side<2; ++side) {
        master = side == 0;
        indicators();
    }
}

int main(void) {
    effect_params_t params = {.init=true};
    solid_result = true;
    assert(CRISBOARD_UNIFORM(&params));
    assert(solid_calls == 1 && last_params == &params);
    solid_result = false;
    assert(!CRISBOARD_UNIFORM(&params) && solid_calls == 2);

    // Every existing mode retains the complete original result on both halves.
    for (mode=1; mode<=RGB_MATRIX_CYCLE_UP_DOWN; ++mode) {
        for (unsigned layout=0; layout<2; ++layout) {
            default_layer_state = 1u << layout;
            for (unsigned fn=0; fn<2; ++fn) {
                layer_state = fn ? 1u << _LOWER : 0;
                RGB expected[68];
                render(original_rgb_matrix_indicators_user);
                memcpy(expected,leds,sizeof(expected));
                render(rgb_matrix_indicators_user);
                assert(memcmp(expected,leds,sizeof(expected)) == 0);
            }
        }
    }
    mode = RGB_MATRIX_CUSTOM_CRISBOARD_UNIFORM;
    for (unsigned layout=0; layout<2; ++layout) {
        default_layer_state = 1u << layout;
        for (unsigned fn=0; fn<2; ++fn) {
            layer_state = fn ? 1u << _LOWER : 0;
            render(rgb_matrix_indicators_user);
            for (unsigned i=0; i<68; ++i) {
                HSV expected = base;
                if (fn && ((i>=28 && i<=33) || (i>=62 && i<=67)))
                    expected.h = (uint8_t)((base.h+50)%255);
                RGB color = hsv_to_rgb(expected);
                assert(memcmp(&leds[i],&color,sizeof(color)) == 0);
            }
        }
    }
    puts("PASS: actual indicator callbacks; all old modes identical; Uniform covers both halves; temporary Fn indicators preserved; shared solid renderer.");
    return 0;
}
