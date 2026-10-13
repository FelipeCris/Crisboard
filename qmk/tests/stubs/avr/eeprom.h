// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <stddef.h>
#include <stdint.h>
#define E2END 1023
void eeprom_read_block(void *dst, const void *src, size_t size);
void eeprom_update_block(const void *src, void *dst, size_t size);
void eeprom_update_byte(uint8_t *dst, uint8_t value);
