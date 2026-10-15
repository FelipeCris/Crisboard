"""Execute actual preset code and native output selection on a host compiler."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

zmk = Path(sys.argv[1]).resolve()
stubs = r'''
#pragma once
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <zmk/crisboard_rgb_presets.h>
#define BIT(n) (1u << (n))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define K_NO_WAIT 0
#define K_MSEC(x) (x)
#define ZMK_BLE_IS_CENTRAL 1
#define ZMK_BLE_SPLIT_PERIPHERAL_COUNT 1
#define ZMK_BEHAVIOR_OPAQUE 0
#define ZMK_EV_EVENT_BUBBLE 0
#define LOG_MODULE_DECLARE(...)
#define LOG_ERR(...)
#define LOG_WRN(...)
#define ZMK_LISTENER(...)
#define ZMK_SUBSCRIPTION(...)
#define DEVICE_DT_INST_DEFINE(...)
struct device { int unused; };
typedef void zmk_event_t;
struct zmk_behavior_binding { const char *behavior_dev; uint32_t param1, param2; };
struct zmk_behavior_binding_event { uint8_t layer; uint32_t position; int64_t timestamp; };
enum behavior_locality { BEHAVIOR_LOCALITY_CENTRAL };
struct behavior_driver_api {
    enum behavior_locality locality;
    int (*binding_pressed)(struct zmk_behavior_binding *, struct zmk_behavior_binding_event);
    int (*binding_released)(struct zmk_behavior_binding *, struct zmk_behavior_binding_event);
};
struct k_work { void (*handler)(struct k_work *); bool queued; };
struct k_work_delayable { struct k_work work; int64_t due; };
struct k_msgq { size_t item_size; unsigned head, tail, count; uint8_t data[8][64]; };
#define K_WORK_DEFINE(n,f) struct k_work n = {.handler = f}
#define K_MSGQ_DEFINE(n,s,max,align) struct k_msgq n = {.item_size = s}
static int64_t now;
static bool fn_active, on_system_work;
static uint32_t rgb_snapshot;
static unsigned writes, local_loads, peripheral_loads;
static uint32_t peripheral_snapshot;
static uint8_t saved_records[5][8];
static bool saved_valid[5];
static int save_error;
static int64_t k_uptime_get(void) { return now; }
static bool zmk_keymap_layer_active(uint8_t layer) { assert(layer == 2); return fn_active; }
static void k_work_init_delayable(struct k_work_delayable *w, void (*f)(struct k_work *)) { w->work.handler = f; }
static int k_work_reschedule(struct k_work_delayable *w, int64_t delay) { w->due = now + delay; w->work.queued = true; return 1; }
static int k_work_cancel_delayable(struct k_work_delayable *w) { w->work.queued = false; return 0; }
static int k_work_submit(struct k_work *w) { w->queued = true; return 1; }
static int k_msgq_put(struct k_msgq *q, const void *value, int timeout) {
    assert(timeout == 0 && q->item_size <= 64);
    if (q->count == 8) return -ENOSPC;
    memcpy(q->data[q->tail], value, q->item_size); q->tail = (q->tail + 1) % 8; q->count++; return 0;
}
static int k_msgq_get(struct k_msgq *q, void *value, int timeout) {
    assert(timeout == 0);
    if (!q->count) return -ENOMSG;
    memcpy(value, q->data[q->head], q->item_size); q->head = (q->head + 1) % 8; q->count--; return 0;
}
typedef ssize_t (*settings_read_cb)(void *, void *, size_t);
struct settings_handler { const char *name; int (*h_set)(const char *, size_t, settings_read_cb, void *); };
static void settings_subsys_init(void) {}
static int settings_register(struct settings_handler *h) { assert(!strcmp(h->name,"crisboard_rgb")); return 0; }
static int settings_load_subtree(const char *name) { assert(!strcmp(name,"crisboard_rgb")); return 0; }
static int settings_save_one(const char *name, const void *value, size_t length) {
    assert(on_system_work && length == 8);
    const char *prefix = "crisboard_rgb/p";
    assert(!strncmp(name, prefix, strlen(prefix)));
    unsigned slot = name[strlen(prefix)] - '0'; assert(slot < 5);
    if (save_error) return save_error;
    memcpy(saved_records[slot], value, 8); saved_valid[slot] = true; writes++; return 0;
}
static int zmk_rgb_underglow_get_snapshot(uint32_t *value) { *value = rgb_snapshot; return 0; }
static int behavior_keymap_binding_pressed(struct zmk_behavior_binding *b, struct zmk_behavior_binding_event e) {
    assert(!strcmp(b->behavior_dev,"RGB_UG") && b->param1 == CRISBOARD_RGB_APPLY_CMD);
    assert(crisboard_rgb_valid(b->param2, CRISBOARD_RGB_EFFECT_COUNT)); rgb_snapshot = b->param2; local_loads++; return 0;
}
static int zmk_split_bt_invoke_behavior(uint8_t side, struct zmk_behavior_binding *b, struct zmk_behavior_binding_event e, bool pressed) {
    assert(side == 0 && pressed && b->param1 == CRISBOARD_RGB_APPLY_CMD);
    peripheral_snapshot = b->param2; peripheral_loads++; return 0;
}
'''
tests = r'''
static void drain(void) {
    on_system_work = true;
    preset_commands_work.queued = false;
    preset_commands_work.handler(&preset_commands_work);
    on_system_work = false;
}
static void press(unsigned slot, unsigned position) {
    struct zmk_behavior_binding binding = {.param1 = slot};
    struct zmk_behavior_binding_event event = {.layer=2,.position=position,.timestamp=now};
    assert(preset_pressed(&binding,event) == 0); drain();
}
static void release(unsigned slot, unsigned position) {
    struct zmk_behavior_binding binding = {.param1 = slot};
    struct zmk_behavior_binding_event event = {.layer=2,.position=position,.timestamp=now};
    assert(preset_released(&binding,event) == 0); drain();
}
static void tick(void) {
    on_system_work = true;
    hold_work.work.queued = false;
    hold_work.work.handler(&hold_work.work);
    on_system_work = false;
}
static ssize_t read_record(void *context, void *out, size_t length) { memcpy(out,context,length); return length; }
int main(void) {
    assert(preset_init(NULL) == 0);
    for (unsigned slot=0; slot<5; slot++) {
        uint32_t value=crisboard_rgb_pack(360,100,0,5,3,false), decoded=0;
        uint8_t record[8]; crisboard_preset_encode(slot,value,record);
        assert(crisboard_preset_decode(slot,record,CRISBOARD_RGB_EFFECT_COUNT,&decoded) && decoded==value);
        for (unsigned bit=0; bit<64; bit++) {
            record[bit/8] ^= 1u << (bit%8);
            assert(!crisboard_preset_decode(slot,record,CRISBOARD_RGB_EFFECT_COUNT,&decoded));
            record[bit/8] ^= 1u << (bit%8);
        }
    }
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(361,100,100,1,0,true),CRISBOARD_RGB_EFFECT_COUNT));
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(0,101,100,1,0,true),CRISBOARD_RGB_EFFECT_COUNT));
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(0,100,101,1,0,true),CRISBOARD_RGB_EFFECT_COUNT));
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(0,100,100,0,0,true),CRISBOARD_RGB_EFFECT_COUNT));
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(0,100,100,6,0,true),CRISBOARD_RGB_EFFECT_COUNT));
    assert(!crisboard_rgb_valid(crisboard_rgb_pack(0,100,100,1,CRISBOARD_RGB_EFFECT_COUNT,true),CRISBOARD_RGB_EFFECT_COUNT));
    fn_active=true; now=1000;
    // An empty slot has no effect.
    press(0,20); now+=50; release(0,20); assert(writes==0 && local_loads==0);
    // The threshold is exactly 2000 ms; no premature write or load on release.
    rgb_snapshot=crisboard_rgb_pack(180,80,60,4,2,true); uint32_t first=rgb_snapshot;
    now=2000; press(0,20); now=3999; tick(); assert(writes==0);
    now=4000; tick(); assert(writes==1 && valid_slots==1);
    now=4010; release(0,20); assert(local_loads==0);
    // Tap loads the central's absolute state into both halves.
    rgb_snapshot=crisboard_rgb_pack(20,0,20,1,0,false);
    now=5000; press(0,20); now=5050; release(0,20);
    assert(rgb_snapshot==first && peripheral_snapshot==first);
    assert(local_loads==1 && peripheral_loads==1 && writes==1);
    // Saving identical data avoids another settings write.
    now=6000; press(0,20); now=8000; tick(); now++; release(0,20); assert(writes==1);
    // A missed timer still saves on release at the threshold (on the work queue).
    rgb_snapshot=crisboard_rgb_pack(90,30,40,2,1,false);
    now=9000; press(1,21); now=11000; release(1,21); assert(writes==2);
    // Releasing Fn first prevents a long hold from overwriting the slot.
    now=12000; press(0,20); fn_active=false;
    preset_layer_listener(NULL); drain(); now=15000; tick(); release(0,20);
    assert(writes==2 && rgb_snapshot==first);
    // All five records survive reload; saving one leaves the others intact.
    fn_active=true;
    for (unsigned slot=2;slot<5;slot++) {
        now+=3000; rgb_snapshot=crisboard_rgb_pack(slot*20,50,slot*10,slot,slot==4?CRISBOARD_RGB_EFFECT_COUNT-1:slot,true);
        press(slot,20+slot); now+=2000; tick(); release(slot,20+slot);
    }
    assert(writes==5 && valid_slots==31);
    uint32_t expected[5]; memcpy(expected,presets,sizeof(expected));
    memset(presets,0,sizeof(presets)); valid_slots=0;
    for (unsigned slot=0;slot<5;slot++) {
        char name[3]={'p','0'+slot,0}; assert(saved_valid[slot]);
        assert(preset_settings_set(name,8,read_record,saved_records[slot])==0);
        assert(presets[slot]==expected[slot]);
    }
    assert(valid_slots==31);
    // Each restored slot loads the same absolute state into both halves,
    // including the newly appended effect in slot 5.
    for (unsigned slot=0;slot<5;slot++) {
        now+=100; press(slot,20+slot); now+=50; release(slot,20+slot);
        assert(rgb_snapshot==expected[slot] && peripheral_snapshot==expected[slot]);
    }
    assert(writes==5 && local_loads==peripheral_loads);
    uint8_t corrupt[8]; memcpy(corrupt,saved_records[0],8); corrupt[7]^=1;
    assert(preset_settings_set("p0",8,read_record,corrupt)==-EINVAL);
    assert(preset_settings_set("p0",7,read_record,saved_records[0])==-EINVAL);
    assert(presets[0]==expected[0]);
    // Failed storage preserves the older preset and never applies it on long release.
    unsigned before_loads=local_loads; uint32_t before=presets[0]; save_error=-EIO;
    now+=3000; rgb_snapshot=crisboard_rgb_pack(300,100,70,3,0,true);
    press(0,20); now+=2000; tick(); release(0,20);
    assert(presets[0]==before && writes==5 && local_loads==before_loads);
    puts("PASS: actual preset driver, 2000-ms boundary, both-half apply, persistence, CRC, Fn-first release and storage failure.");
}
'''


def function(source, name):
    match = re.search(r'(?m)^(?:static\s+)?[\w\s\*]+\b' + re.escape(name) + r'\([^;]*?\)\s*\{', source)
    assert match, name
    opening = source.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


with tempfile.TemporaryDirectory(prefix='crisboard-fn-tests-') as directory:
    temp = Path(directory)
    (temp / 'test_stubs.h').write_text('#include <sys/types.h>\n' + stubs)
    for name in ['device.h','drivers/behavior.h','kernel.h','logging/log.h','settings/settings.h',
                 'zmk/ble.h','zmk/event_manager.h','zmk/events/layer_state_changed.h',
                 'zmk/keymap.h','zmk/rgb_underglow.h','zmk/split/bluetooth/central.h']:
        path = temp / name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('#include "test_stubs.h"\n')
    driver = zmk / 'app/src/behaviors/behavior_crisboard_rgb_preset.c'
    (temp / 'driver_test.c').write_text('#include "test_stubs.h"\n#include "' + str(driver) + '"\n' + tests)
    flags=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-parameter',
           '-Wno-unused-function','-Wno-unused-variable','-Wno-sign-compare',
           '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',
           '-I'+str(temp),'-I'+str(zmk/'app/include')]
    subprocess.run(flags+[str(temp/'driver_test.c'),'-o',str(temp/'driver_test')],check=True)
    subprocess.run([str(temp/'driver_test')],check=True)
    endpoint_source=(zmk/'app/src/endpoints.c').read_text()
    selection=function(endpoint_source,'get_selected_endpoint')
    program='''#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#define LOG_DBG(...)
enum zmk_endpoint { ZMK_ENDPOINT_USB, ZMK_ENDPOINT_BLE };
#define DEFAULT_ENDPOINT ZMK_ENDPOINT_BLE
static enum zmk_endpoint preferred_endpoint;
static bool usb, ble;
static bool is_usb_ready(void) { return usb; }
static bool is_ble_ready(void) { return ble; }
''' + selection + '''
int main(void) {
    usb=true; ble=false; preferred_endpoint=ZMK_ENDPOINT_BLE;
    assert(get_selected_endpoint()==ZMK_ENDPOINT_USB);
    ble=true; assert(get_selected_endpoint()==ZMK_ENDPOINT_BLE);
    preferred_endpoint=ZMK_ENDPOINT_USB; assert(get_selected_endpoint()==ZMK_ENDPOINT_USB);
    usb=false; assert(get_selected_endpoint()==ZMK_ENDPOINT_BLE);
    puts("PASS: actual endpoint policy retains USB fallback when the selected Bluetooth profile is disconnected.");
}
'''
    (temp/'endpoint_test.c').write_text(program)
    subprocess.run(flags+[str(temp/'endpoint_test.c'),'-o',str(temp/'endpoint_test')],check=True)
    subprocess.run([str(temp/'endpoint_test')],check=True)
