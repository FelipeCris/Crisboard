// SPDX-License-Identifier: GPL-2.0-or-later
// Run the actual firmware module with bounded EEPROM and QMK API stubs.
#include "../keyboards/crisboard/keymaps/default/rgb_presets.h"
#include "eeconfig.h"
#include "avr/eeprom.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct { HSV hsv; uint8_t mode, speed, enabled; } lighting_t;
static lighting_t lighting;
static uint8_t memory[1024];
static unsigned writes[1024], write_count, native_commits;
static int write_budget = -1;
static uint16_t now;
static bool fn = true;
// These stand for the modified HSV copies used to paint Fn and border LEDs.
static HSV hsv, hsv2;

bool layer_state_is(uint8_t layer) { return fn && layer == 2; }
uint16_t timer_read(void) { return now; }
uint16_t timer_elapsed(uint16_t since) { return (uint16_t)(now - since); }
HSV rgb_matrix_get_hsv(void) { return lighting.hsv; }
uint8_t rgb_matrix_get_mode(void) { return lighting.mode; }
uint8_t rgb_matrix_get_speed(void) { return lighting.speed; }
uint8_t rgb_matrix_is_enabled(void) { return lighting.enabled; }
void rgb_matrix_enable(void) { lighting.enabled = 1; }
void rgb_matrix_disable(void) { lighting.enabled = 0; }
void rgb_matrix_mode(uint8_t mode) { if (lighting.enabled) lighting.mode = mode; }
void rgb_matrix_sethsv(uint16_t h, uint8_t s, uint8_t v) {
    if (lighting.enabled) lighting.hsv = (HSV){(uint8_t)h, s, v};
}
void rgb_matrix_set_speed(uint8_t speed) { lighting.speed = speed; }

void eeprom_read_block(void *dst, const void *src, size_t size) {
    size_t address = (uintptr_t)src;
    assert(address + size <= sizeof(memory));
    memcpy(dst, memory + address, size);
}
void eeprom_update_byte(uint8_t *dst, uint8_t value) {
    size_t address = (uintptr_t)dst;
    assert(address < sizeof(memory));
    if (memory[address] == value || write_budget == 0) return;
    if (write_budget > 0) --write_budget;
    memory[address] = value;
    ++writes[address];
    ++write_count;
}
void eeprom_update_block(const void *src, void *dst, size_t size) {
    // AVR libc updates blocks backwards. Signature commit must be safe either way.
    const uint8_t *bytes = src;
    size_t address = (uintptr_t)dst;
    assert(address + size <= sizeof(memory));
    while (size) {
        --size;
        eeprom_update_byte((uint8_t *)(uintptr_t)(address + size), bytes[size]);
    }
}
void eeconfig_update_rgb_matrix(void) {
    ++native_commits;
    uint8_t bytes[] = {(uint8_t)((lighting.mode << 2) | lighting.enabled),
        lighting.hsv.h, lighting.hsv.s, lighting.hsv.v, lighting.speed, 0xFF};
    eeprom_update_block(bytes, (void *)(uintptr_t)28, sizeof(bytes));
}

static void clear_counts(void) {
    memset(writes, 0, sizeof(writes));
    write_count = native_commits = 0;
    write_budget = -1;
}
static bool same(lighting_t a, lighting_t b) {
    return a.hsv.h == b.hsv.h && a.hsv.s == b.hsv.s && a.hsv.v == b.hsv.v &&
        a.mode == b.mode && a.speed == b.speed && a.enabled == b.enabled;
}
static void key(uint8_t slot, bool pressed, uint16_t code) {
    keyrecord_t record = {.event = {.key = {.row = 6, .col = (uint8_t)(5-slot)}, .pressed = pressed}};
    assert(!crisboard_process_rgb_presets(code, &record));
}
static void advance(uint16_t ms) {
    now += ms;
    crisboard_rgb_presets_scan();
}
static void tap(uint8_t slot) {
    key(slot, true, CB_RGB_PRESET_1 + slot);
    advance(100);
    key(slot, false, CB_RGB_PRESET_1 + slot);
}
static void save(uint8_t slot) {
    key(slot, true, CB_RGB_PRESET_1 + slot);
    advance(CB_RGB_PRESET_HOLD_MS);
    key(slot, false, CB_RGB_PRESET_1 + slot);
}
static void assert_save_region_only(void) {
    for (size_t i = 0; i < sizeof(writes)/sizeof(writes[0]); ++i)
        if (i < 64 || i >= 94) assert(writes[i] == 0);
    assert(native_commits == 0);
}

int main(void) {
    const lighting_t a = {{7,201,137},3,81,1};
    const lighting_t b = {{161,43,29},5,190,1};
    const lighting_t off = {{30,120,90},4,60,0};
    memset(memory, 0xFF, sizeof(memory));
    lighting = a;
    clear_counts();
    for (uint8_t slot = 0; slot < 3; ++slot) tap(slot);
    assert(same(lighting,a) && write_count == 0 && native_commits == 0);

    // Fn and border HSV copies differ: saving while Fn is held must capture a.
    hsv = (HSV){57,201,137};
    hsv2 = (HSV){134,201,137};
    assert(hsv.h != a.hsv.h && hsv2.h != a.hsv.h);
    key(0,true,CB_RGB_PRESET_1);
    advance(1999);
    assert(write_count == 0);
    advance(1);
    assert(write_count > 0);
    assert_save_region_only();
    unsigned once = write_count;
    for (unsigned i=0; i<1000; ++i) advance(100);
    assert(write_count == once);
    key(0,false,CB_RGB_PRESET_1);
    assert(native_commits == 0); // A long hold must not load on release.
    uint8_t slots[30]; memcpy(slots,memory+64,sizeof(slots));
    lighting = b;
    clear_counts();
    tap(0);
    assert(same(lighting,a) && native_commits == 1);
    assert(memcmp(slots,memory+64,sizeof(slots)) == 0);
    for (unsigned i=64; i<94; ++i) assert(writes[i] == 0);
    clear_counts();
    save(0);
    assert(write_count == 0); // Identical saves avoid unnecessary EEPROM writes.

    lighting = b; save(1);
    lighting = off; save(2);
    lighting = off; tap(1);
    assert(same(lighting,b)); // Loading must work with RGB initially off.
    lighting = a; tap(2);
    assert(same(lighting,off)); // Off presets still restore HSV/mode/speed.
    lighting = b; tap(0);
    assert(same(lighting,a)); // Independent slots, no lighting cache.

    // Fn release first must not leave a pending key or accidentally save.
    clear_counts(); lighting = b;
    key(0,true,CB_RGB_PRESET_1);
    advance(500); fn=false; advance(3000);
    assert(write_count == 0);
    key(0,false,0x0D); // Base J rather than the preset code on key release.
    assert(same(lighting,a));
    fn=true;

    now=65500; lighting=b;
    save(1); // Timer wrap.
    lighting=a; tap(1); assert(same(lighting,b));

    // Empty, corrupted and version-mismatched slots leave RGB untouched.
    uint8_t valid[10]; memcpy(valid,memory+64,10);
    memory[67] ^= 1;
    clear_counts(); lighting=b; tap(0);
    assert(same(lighting,b) && native_commits == 0 && write_count == 0);
    memcpy(memory+64,valid,10); ++memory[66];
    tap(0); assert(same(lighting,b) && native_commits == 0);
    memcpy(memory+64,valid,10);

    // Every possible interrupted save either retains the old record or is
    // rejected, never applies partial RGB data, and never touches other areas.
    uint8_t original[1024]; memcpy(original,memory,sizeof(memory));
    clear_counts(); lighting=b; save(0);
    unsigned complete_writes=write_count;
    for (unsigned cut=0; cut<complete_writes; ++cut) {
        memcpy(memory,original,sizeof(memory)); clear_counts();
        lighting=b; write_budget=(int)cut; save(0);
        assert_save_region_only();
        write_budget=-1; lighting=off; native_commits=0; tap(0);
        assert(same(lighting, cut==0 ? a : off));
        for (unsigned i=0;i<1024;++i)
            if ((i<28 || i>=34) && (i<64 || i>=74)) assert(memory[i]==original[i]);
    }

    // Simultaneous preset keys: only the first held key can save.
    memset(memory+64,0xFF,30); clear_counts(); lighting=a;
    key(0,true,CB_RGB_PRESET_1); key(1,true,CB_RGB_PRESET_2);
    advance(2000); key(1,false,CB_RGB_PRESET_2); key(0,false,CB_RGB_PRESET_1);
    for (unsigned i=74;i<94;++i) assert(memory[i]==0xFF);
    lighting=b; tap(0); assert(same(lighting,a));

    // The appended Uniform mode uses the existing record and persistence path.
    const lighting_t uniform = {{83,217,99},RGB_MATRIX_CUSTOM_CRISBOARD_UNIFORM,72,1};
    lighting=uniform; save(2);
    lighting=b; tap(2); assert(same(lighting,uniform));

    keyrecord_t other={.event={.key={.row=0,.col=0},.pressed=true}};
    assert(crisboard_process_rgb_presets(4,&other));
    puts("PASS: actual preset module; base color excludes Fn indicators; three slots; hold/tap; disabled RGB; EEPROM bounds; corrupt/interrupted saves; timer wrap; Fn-first release.");
    return 0;
}
