// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define SAFE_RANGE 0x5DB2
#define RGB_MATRIX_EFFECT_MAX 8
typedef struct { uint8_t h, s, v; } HSV;
typedef struct { uint8_t row, col; } keypos_t;
typedef struct { keypos_t key; bool pressed; } keyevent_t;
typedef struct { keyevent_t event; } keyrecord_t;
bool layer_state_is(uint8_t layer);
uint16_t timer_read(void);
uint16_t timer_elapsed(uint16_t since);
HSV rgb_matrix_get_hsv(void);
uint8_t rgb_matrix_get_mode(void);
uint8_t rgb_matrix_get_speed(void);
uint8_t rgb_matrix_is_enabled(void);
void rgb_matrix_enable(void);
void rgb_matrix_disable(void);
void rgb_matrix_mode(uint8_t mode);
void rgb_matrix_sethsv(uint16_t hue, uint8_t saturation, uint8_t value);
void rgb_matrix_set_speed(uint8_t speed);
