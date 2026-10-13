/* Copyright
 *   2021 solartempest
 *   2021 QMK
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once
#include "config_common.h"

#define MASTER_RIGHT
// Key matrix size
// Rows are doubled-up.
#define MATRIX_ROWS  10
#define MATRIX_COLS  7

// wiring of each half
#define MATRIX_ROW_PINS       { B2, B6, C6, D7, E6 }
#define MATRIX_COL_PINS       { B3, B1, F7, F6, F4, F5, D4 }
#define MATRIX_ROW_PINS_RIGHT { B2, B6, C6, D7, E6 }
#define MATRIX_COL_PINS_RIGHT { B3, B1, F7, F6, F4, F5, D4 }


#define DIODE_DIRECTION COL2ROW

#define DEBOUNCE        5

// Communication between sides
#define SOFT_SERIAL_PIN D2

// OLED settings
#define OLED_TIMEOUT    80000
#define OLED_BRIGHTNESS 90

#define SPLIT_WPM_ENABLE
#define SPLIT_OLED_ENABLE
#define SPLIT_TRANSPORT_MIRROR
//#define SPLIT_MODS_ENABLE
#define SPLIT_LAYER_STATE_ENABLE

// Add RGB underglow
// by defining in the keyboard, incompatible keymaps will fail to compile.
#ifdef RGB_MATRIX_ENABLE
#    define RGB_DI_PIN D3
#    define RGBLED_NUM 68
#    define RGBLIGHT_LIMIT_VAL 100 // LED Brightness, high power draw may exceed the USB limitations of 0.6A and cause a crash.
#    define RGBLIGHT_HUE_STEP  5
#    define RGBLIGHT_SAT_STEP  10
#    define RGBLIGHT_VAL_STEP  10
#    define RGBLIGHT_LAYERS //Enable layer light indicators. Not required as updates are done in layer_state_set_user and led_update_user (+588).
#    define RGBLIGHT_SLEEP //Turn off LEDs when computer sleeping (+72)
#    define RGBLIGHT_LAYERS_RETAIN_VAL

#    define RGB_MATRIX_SPLIT {34,34}
#    define DRIVER_LED_TOTAL RGBLED_NUM 

#define RGB_MATRIX_IDLE_TIMEOUT 1000 * 30
#define RGB_DISABLE_TIMEOUT 1000 * 60 * 30
#define RGB_DISABLE_WHEN_USB_SUSPENDED

#define DYNAMIC_KEYMAP_LAYER_COUNT 8
#define DYNAMIC_KEYMAP_MACRO_COUNT 5

#define RGB_MATRIX_MAXIMUM_BRIGHTNESS 100

#define OLED_FONT_H "keyboards/crisboard/lib/crislogo.c"
#define NO_ACTION_ONESHOT


// Enable animations

 #  define ENABLE_RGB_MATRIX_GRADIENT_UP_DOWN            // Static gradient top to bottom speed controls how much gradient changes
 #  define ENABLE_RGB_MATRIX_BREATHING                   // Single hue brightness cycling animation
 //#  define ENABLE_RGB_MATRIX_BAND_VAL                    // Single hue band fading brightness scrolling left to right
 #  define ENABLE_RGB_MATRIX_BAND_SPIRAL_VAL             // Single hue spinning spiral fades brightness
 #  define ENABLE_RGB_MATRIX_CYCLE_UP_DOWN               // Full gradient scrolling top to bottom
// #  define ENABLE_RGB_MATRIX_CYCLE_OUT_IN                // Full gradient scrolling out to in
 #  define ENABLE_RGB_MATRIX_CYCLE_SPIRAL                // Full gradient spinning spiral around center of keyboard
// #  define ENABLE_RGB_MATRIX_RAINBOW_PINWHEELS           // Full dual gradients spinning two halfs of keyboard
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_WIDE         // Hue & value pulse near a single key hit then fades value out
 //#  define RGB_MATRIX_FRAMEBUFFER_EFFECTS // Required for the following two effects
 //#  define ENABLE_RGB_MATRIX_TYPING_HEATMAP               // How hot is your WPM!


 //#  define ENABLE_RGB_MATRIX_CYCLE_OUT_IN_DUAL           // Full dual gradients scrolling out to in
// #  define ENABLE_RGB_MATRIX_BAND_PINWHEEL_VAL           // Single hue 3 blade spinning pinwheel fades brightness
 //#  define ENABLE_RGB_MATRIX_ALPHAS_MODS                 // Static dual hue speed is hue for secondary hue
 //#  define ENABLE_RGB_MATRIX_GRADIENT_LEFT_RIGHT         // Static gradient left to right speed controls how much gradient changes
 //#  define ENABLE_RGB_MATRIX_BAND_SAT                    // Single hue band fading saturation scrolling left to right
 //#  define ENABLE_RGB_MATRIX_BAND_PINWHEEL_SAT           // Single hue 3 blade spinning pinwheel fades saturation
 //#  define ENABLE_RGB_MATRIX_BAND_SPIRAL_SAT             // Single hue spinning spiral fades saturation
 //#  define ENABLE_RGB_MATRIX_CYCLE_ALL                   // Full keyboard solid hue cycling through full gradient
 //#  define ENABLE_RGB_MATRIX_CYCLE_LEFT_RIGHT            // Full gradient scrolling left to right

 //#  define ENABLE_RGB_MATRIX_RAINBOW_MOVING_CHEVRON      // Full gradent Chevron shapped scrolling left to right
 //#  define ENABLE_RGB_MATRIX_CYCLE_PINWHEEL              // Full gradient spinning pinwheel around center of keyboard

 
 //#  define ENABLE_RGB_MATRIX_DUAL_BEACON                 // Full gradient spinning around center of keyboard
 //#  define ENABLE_RGB_MATRIX_RAINBOW_BEACON              // Full tighter gradient spinning around center of keyboard
 //#  define ENABLE_RGB_MATRIX_RAINDROPS                   // Randomly changes a single key's hue
 //#  define ENABLE_RGB_MATRIX_JELLYBEAN_RAINDROPS         // Randomly changes a single key's hue and saturation
 //#  define ENABLE_RGB_MATRIX_HUE_BREATHING               // Hue shifts up a slight ammount at the same time then shifts back
 //#  define ENABLE_RGB_MATRIX_HUE_PENDULUM                // Hue shifts up a slight ammount in a wave to the right then back to the left
 //#  define ENABLE_RGB_MATRIX_HUE_WAVE                          // Hue shifts up a slight ammount and then back down in a wave to the right

// #  define ENABLE_RGB_MATRIX_DIGITAL_RAIN                 // That famous computer simulation
 //#    define RGB_MATRIX_KEYPRESSES // reacts to keypresses, required for the remaining effects
 //#    define RGB_MATRIX_KEYRELEASES // reacts to keyreleases (instead of keypresses)
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_SIMPLE       // Pulses keys hit to hue & value then fades value out
 //#  define ENABLE_RGB_MATRIX_SOLID_REACTIVE              // Static single hue pulses keys hit to shifted hue then fades to current hue

// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_MULTIWIDE    // Hue & value pulse near multiple key hits then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_CROSS        // Hue & value pulse the same column and row of a single key hit then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_MULTICROSS   // Hue & value pulse the same column and row of multiple key hits then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_NEXUS        // Hue & value pulse away on the same column and row of a single key hit then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_REACTIVE_MULTINEXUS   // Hue & value pulse away on the same column and row of multiple key hits then fades value out
// #  define ENABLE_RGB_MATRIX_SPLASH                      // Full gradient & value pulse away from a single key hit then fades value out
// #  define ENABLE_RGB_MATRIX_MULTISPLASH                 // Full gradient & value pulse away from multiple key hits then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_SPLASH                // Hue & value pulse away from a single key hit then fades value out
// #  define ENABLE_RGB_MATRIX_SOLID_MULTISPLASH           // Hue & value pulse away from multiple key hits then fades value out




#endif


#define USE_SERIAL




