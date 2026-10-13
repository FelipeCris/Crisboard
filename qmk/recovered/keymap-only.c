// SPDX-License-Identifier: GPL-2.0-or-later
// Reconstructed keymap ONLY; not the complete installed firmware source.
// Both verified USB halves contain this same 420-byte table.
// Legacy QMK symbols: see ../README.md before attempting a build.
#include QMK_KEYBOARD_H

enum recovered_layers { _COLEMAK, _QWERTY, _LOWER };

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_COLEMAK] = LAYOUT(
        KC_ESC, KC_1, KC_2, KC_3, KC_4, KC_5,    KC_6, KC_7, KC_8, KC_9, KC_0, KC_DEL,
        KC_CAPS, KC_Q, KC_W, KC_F, KC_P, KC_G, KC_GRV,    KC_RBRC, KC_J, KC_L, KC_U, KC_Y, KC_SCLN, KC_BSPC,
        KC_TAB, KC_A, KC_R, KC_S, KC_T, KC_D, KC_NO,    KC_ALGR, KC_H, KC_N, KC_E, KC_I, KC_O, KC_DOT,
        KC_LSFT, KC_NONUS_BACKSLASH, KC_Z, KC_X, KC_C, KC_V, KC_SPC,    KC_ENT, KC_B, KC_K, KC_M, KC_SLSH, KC_UP, KC_MINUS,
        KC_LCTRL, MO(_LOWER), KC_LGUI, KC_LALT, KC_LBRC, KC_COMM, KC_HOME,    KC_END, KC_SPC, KC_QUOT, KC_BSLS, KC_LEFT, KC_DOWN, KC_RIGHT
    ),
    [_QWERTY] = LAYOUT(
        KC_ESC, KC_1, KC_2, KC_3, KC_4, KC_5,    KC_6, KC_7, KC_8, KC_9, KC_0, KC_DEL,
        KC_CAPS, KC_Q, KC_W, KC_E, KC_R, KC_T, KC_GRV,    KC_RBRC, KC_Y, KC_U, KC_I, KC_O, KC_P, KC_BSPC,
        KC_TAB, KC_A, KC_S, KC_D, KC_F, KC_G, KC_NO,    KC_ALGR, KC_H, KC_J, KC_K, KC_L, KC_SCLN, KC_LBRC,
        KC_LSFT, KC_NONUS_BACKSLASH, KC_Z, KC_X, KC_C, KC_V, KC_SPC,    KC_ENT, KC_B, KC_N, KC_M, KC_SLSH, KC_UP, KC_MINUS,
        KC_LCTRL, MO(_LOWER), KC_LGUI, KC_LALT, KC_DOT, KC_COMM, KC_HOME,    KC_END, KC_SPC, KC_QUOT, KC_BSLS, KC_LEFT, KC_DOWN, KC_RIGHT
    ),
    [_LOWER] = LAYOUT(
        RGB_TOG, KC_F1, KC_F2, KC_F3, KC_F4, KC_F5,    KC_F6, KC_F7, KC_F8, KC_F9, KC_F10, KC_F11,
        KC_CAPS, KC_Q, KC_W, KC_E, KC_R, KC_T, DF(_QWERTY),    DF(_COLEMAK), KC_NO, KC_MUTE, KC_MPLY, KC_O, KC_P, KC_F12,
        KC_TAB, KC_A, KC_S, KC_D, KC_F, KC_G, KC_NO,    KC_NO, KC_H, KC_J, KC_K, KC_L, KC_SCLN, KC_DOT,
        KC_LSFT, KC_NONUS_BACKSLASH, KC_Z, KC_X, KC_C, KC_V, KC_PSCR,    KC_ENT, KC_B, KC_N, KC_NO, RGB_SPD, RGB_MODE_FORWARD, RGB_SPI,
        KC_LCTRL, KC_LGUI, KC_NO, KC_LALT, KC_LBRC, KC_COMM, KC_HOME,    KC_END, KC_SPC, KC_QUOT, KC_BSLS, RGB_VAI, RGB_SAI, RGB_HUI
    ),
};
