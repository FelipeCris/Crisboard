"""Compile the actual patched C with host stubs to check battery behavior."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

zmk = Path(sys.argv[1]).resolve()
common = r'''
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
#define IS_ENABLED(x) (x)
#define CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_VOLTAGE 1
#define CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_PERCENTAGE 1
#define CONFIG_USB_DEVICE_STACK 1
#define CONFIG_ZMK_BATTERY_REPORT_INTERVAL 60
#define CONFIG_APPLICATION_INIT_PRIORITY 90
#define CONFIG_ZMK_LOG_LEVEL 0
#define LOG_MODULE_DECLARE(...)
#define LOG_DBG(...)
#define LOG_WRN(...)
#define LOG_ERR(...)
struct device { const char *name; };
extern const struct device test_device;
#define DT_HAS_CHOSEN(x) 1
#define DT_CHOSEN(x) 0
#define DEVICE_DT_GET(x) (&test_device)
static inline bool device_is_ready(const struct device *d) { return true; }
struct sensor_value { int32_t val1, val2; };
enum sensor_channel { SENSOR_CHAN_GAUGE_STATE_OF_CHARGE, SENSOR_CHAN_GAUGE_VOLTAGE };
int sensor_sample_fetch_chan(const struct device *, enum sensor_channel);
int sensor_channel_get(const struct device *, enum sensor_channel, struct sensor_value *);
int bt_bas_set_battery_level(uint8_t);
struct zmk_battery_state_changed { uint8_t state_of_charge; };
static inline struct zmk_battery_state_changed new_zmk_battery_state_changed(struct zmk_battery_state_changed s) { return s; }
int test_raise(struct zmk_battery_state_changed);
#define ZMK_EVENT_RAISE(e) test_raise(e)
struct k_work { int unused; };
struct k_timer { int unused; };
#define K_WORK_DEFINE(name, callback) struct k_work name
#define K_TIMER_DEFINE(name, callback, stop) struct k_timer name
static inline void k_work_submit(struct k_work *w) {}
static inline void k_timer_start(struct k_timer *t, int a, int b) {}
#define K_MINUTES(x) ((x)*60)
#define K_SECONDS(x) (x)
#define SYS_INIT(...)
'''
harness = r'''
#include "common.h"
#include BATTERY_SOURCE
const struct device test_device = {"test"};
static int samples, notifications, events;
static int sample_error, soc_error, voltage_error;
static int measured_mv = 3850;
static uint8_t estimated_pct = 55, bluetooth_pct, event_pct;
int sensor_sample_fetch_chan(const struct device *d, enum sensor_channel chan) {
    assert(chan == SENSOR_CHAN_GAUGE_STATE_OF_CHARGE);
    samples++; return sample_error;
}
int sensor_channel_get(const struct device *d, enum sensor_channel chan, struct sensor_value *v) {
    if (chan == SENSOR_CHAN_GAUGE_STATE_OF_CHARGE) {
        v->val1 = estimated_pct; v->val2 = 0; return soc_error;
    }
    assert(chan == SENSOR_CHAN_GAUGE_VOLTAGE);
    if (voltage_error) return voltage_error;
    v->val1 = measured_mv / 1000; v->val2 = (measured_mv % 1000) * 1000;
    return 0;
}
int bt_bas_set_battery_level(uint8_t pct) { notifications++; bluetooth_pct = pct; return 0; }
int test_raise(struct zmk_battery_state_changed e) { events++; event_pct = e.state_of_charge; return 0; }
int main(void) {
    assert(zmk_battery_voltage_mv() == -1);
    assert(zmk_battery_update(&test_device) == 0);
    assert(samples == 1 && notifications == 1 && events == 1);
    assert(bluetooth_pct == 55 && event_pct == 55 && zmk_battery_voltage_mv() == 3850);
    measured_mv = 3855;
    assert(zmk_battery_update(&test_device) == 0);
    assert(samples == 2 && notifications == 1 && events == 2);
    assert(zmk_battery_voltage_mv() == 3855 && event_pct == 55);
    assert(zmk_battery_update(&test_device) == 0);
    assert(samples == 3 && notifications == 1 && events == 2);
    sample_error = -EIO;
    assert(zmk_battery_update(&test_device) == -EIO);
    assert(samples == 4 && notifications == 1 && events == 2 && zmk_battery_voltage_mv() == 3855);
    sample_error = 0; voltage_error = -EIO; estimated_pct = 56;
    assert(zmk_battery_update(&test_device) == 0);
    assert(samples == 5 && notifications == 2 && events == 3);
    assert(bluetooth_pct == 56 && zmk_battery_voltage_mv() == 3855);
    voltage_error = 0; soc_error = -EIO; measured_mv = 4000;
    assert(zmk_battery_update(&test_device) == -EIO);
    assert(samples == 6 && notifications == 2 && events == 3 && zmk_battery_voltage_mv() == 3855);
    soc_error = 0;
    assert(zmk_battery_update(&test_device) == 0);
    assert(samples == 7 && notifications == 2 && events == 4 && zmk_battery_voltage_mv() == 4000);
    puts("PASS: cached voltage, voltage-only updates, unchanged BLE percentage, one ADC sample, error retention.");
}
'''
widget = (zmk / 'app/src/display/widgets/battery_status.c').read_text()
def block(needle):
    start = widget.index(needle)
    first = widget.index('{', start)
    depth = 1
    end = first + 1
    while depth:
        depth += (widget[end] == '{') - (widget[end] == '}')
        end += 1
    return widget[start:end]
format_harness = r'''
#include "common.h"
typedef struct { int unused; } lv_obj_t;
#define LV_SYMBOL_CHARGE "\xEF\x83\xA7"
#define LV_ALIGN_IN_TOP_RIGHT 0
static char rendered[64];
static void lv_label_set_text(lv_obj_t *o, const char *s) { snprintf(rendered, sizeof(rendered), "%s", s); }
static void lv_obj_align(lv_obj_t *o, void *p, int a, int x, int y) {}
''' + block('struct battery_status_state {') + ';\n' + block('static void set_battery_symbol(') + r'''
static void check(int32_t mv, bool usb, const char *expected) {
    lv_obj_t label;
    set_battery_symbol(&label, (struct battery_status_state){.voltage_mv=mv, .usb_present=usb});
    assert(strcmp(rendered, expected) == 0);
}
int main(void) {
    check(-1, false, "--.-- V");
    check(4080, false, "4.08 V");
    check(4095, false, "4.10 V");
    check(4200, false, "4.20 V");
    check(0, false, "0.00 V");
    check(65535, false, "65.54 V");
    check(4080, true, LV_SYMBOL_CHARGE " 4.08 V");
    check(-1, true, LV_SYMBOL_CHARGE " --.-- V");
    puts("PASS: actual OLED formatter, rounding, unavailable reading, USB glyph, bounded integer formatting.");
}
'''
with tempfile.TemporaryDirectory(prefix='zmk-voltage-test-') as dirname:
    temp = Path(dirname)
    (temp / 'common.h').write_text(common)
    for name in ['device.h', 'devicetree.h', 'init.h', 'kernel.h', 'drivers/sensor.h',
                 'bluetooth/services/bas.h', 'logging/log.h', 'zmk/event_manager.h',
                 'zmk/events/battery_state_changed.h']:
        path = temp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('#include "common.h"\n')
    harness = harness.replace('BATTERY_SOURCE', json.dumps(str(zmk / 'app/src/battery.c')))
    for name, content in [('battery', harness), ('format', format_harness)]:
        source = temp / f'{name}.c'
        source.write_text(content)
        binary = temp / name
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function',
                        '-Wno-unused-parameter', '-fsanitize=address,undefined', '-I', str(temp),
                        '-I', str(zmk / 'app/include'), str(source), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
