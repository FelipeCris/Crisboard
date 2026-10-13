// SPDX-License-Identifier: GPL-2.0-or-later
// No include guard: QMK includes this file for the enum, renderer and dispatch.
RGB_MATRIX_EFFECT(CRISBOARD_UNIFORM)

#ifdef RGB_MATRIX_CUSTOM_EFFECT_IMPLS
// Append the mode after the five existing effects, preserving saved mode IDs.
_Static_assert(RGB_MATRIX_SOLID_COLOR == 1 && RGB_MATRIX_GRADIENT_UP_DOWN == 2 &&
               RGB_MATRIX_BREATHING == 3 && RGB_MATRIX_BAND_SPIRAL_VAL == 4 &&
               RGB_MATRIX_CYCLE_UP_DOWN == 5 && RGB_MATRIX_CUSTOM_CRISBOARD_UNIFORM == 6 &&
               RGB_MATRIX_EFFECT_MAX == 7, "Review stored preset modes after changing effects");

static bool CRISBOARD_UNIFORM(effect_params_t *params) {
    // Reuse the same renderer, limits and split handling as QMK's solid effect.
    return SOLID_COLOR(params);
}
#endif
