"""Reproduce idle -> settings -> reboot with actual native RGB functions."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

zmk = Path(sys.argv[1]).resolve()
baseline = Path(sys.argv[2]).read_text()
target = (zmk / 'app/src/rgb_underglow.c').read_text()


def function(text, name):
    found = re.search(r'(?m)^(?:static\s+)?[\w\s\*]+\b' + name + r'\([^;]*?\)\s*\{', text)
    assert found, name
    opening = text.index('{', found.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[found.start():end]


prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <zmk/crisboard_rgb_presets.h>
#define IS_ENABLED(x) x
#define CONFIG_SETTINGS 1
#define CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER 0
#define CONFIG_ZMK_RGB_UNDERGLOW_AUTO_OFF_USB 0
#define CONFIG_ZMK_RGB_UNDERGLOW_HUE_START 0
#define CONFIG_ZMK_RGB_UNDERGLOW_SAT_START 100
#define CONFIG_ZMK_RGB_UNDERGLOW_BRT_START 100
#define CONFIG_ZMK_RGB_UNDERGLOW_SPD_START 3
#define CONFIG_ZMK_RGB_UNDERGLOW_EFF_START 0
#define CONFIG_ZMK_RGB_UNDERGLOW_ON_START 1
#define CONFIG_ZMK_SETTINGS_SAVE_DEBOUNCE 60000
#define STRIP_LABEL "WS2812"
#define STRIP_NUM_PIXELS 34
#define LOG_INF(...)
#define LOG_ERR(...)
#define K_NO_WAIT 0
#define K_MSEC(x) (x)
#define BIT(x) (1u<<(x))
#define MIN(a,b) ((a)<(b)?(a):(b))
struct device { int unused; } device;
struct zmk_led_hsb { uint16_t h; uint8_t s,b; };
struct led_rgb { uint8_t r,g,b; };
struct k_work { int unused; };
struct k_work_delayable { int unused; };
struct k_timer { int unused; } underglow_tick;
static struct k_work_delayable underglow_save_work;
static struct led_rgb pixels[34];
static const struct device *led_strip;
static bool rgb_suspended, timer_running, pending_save, previous_state;
static unsigned writes, strip_updates;
typedef int (*settings_read_cb)(void *,void *,size_t);
struct settings_handler { const char *name; int (*h_set)(const char *,size_t,settings_read_cb,void *); };
static struct settings_handler rgb_conf;
static int settings_subsys_init(void) { return 0; }
static int settings_register(struct settings_handler *h) { assert(h==&rgb_conf); return 0; }
static bool settings_name_steq(const char *a,const char *b,const char **next) { *next=NULL; return !strcmp(a,b); }
static const struct device *device_get_binding(const char *s) { assert(!strcmp(s,STRIP_LABEL)); return &device; }
static void k_work_init_delayable(struct k_work_delayable *w,void (*f)(struct k_work *)) { (void)w;(void)f; }
static int k_work_reschedule(struct k_work_delayable *w,unsigned ms) { assert(w==&underglow_save_work && ms==60000); pending_save=true; return 1; }
static void k_timer_start(struct k_timer *t,unsigned first,unsigned period) { assert(t==&underglow_tick && first==0 && period==50); timer_running=true; }
static void k_timer_stop(struct k_timer *t) { assert(t==&underglow_tick); timer_running=false; }
static int led_strip_update_rgb(const struct device *d,struct led_rgb *p,size_t n) { assert(d==led_strip && p==pixels && n==34); strip_updates++; return 0; }
'''
settings = r'''
static struct rgb_underglow_state state, saved;
static int read_saved(void *arg,void *destination,size_t size) { assert(arg==&saved && size==sizeof(saved)); memcpy(destination,&saved,size); return size; }
static int settings_load_subtree(const char *name) { assert(!strcmp(name,"rgb/underglow")); return rgb_conf.h_set("state",sizeof(saved),read_saved,&saved); }
static int settings_save_one(const char *name,const void *data,size_t size) { assert(!strcmp(name,"rgb/underglow/state") && size==sizeof(saved)); memcpy(&saved,data,size); writes++; return 0; }
'''
main = r'''
static void flush(void) { if(pending_save) { pending_save=false; zmk_rgb_underglow_save_state_work(); } }
static void reboot(void) {
    timer_running=false; pending_save=false; previous_state=false; rgb_suspended=false;
    rgb_conf=(struct settings_handler){.name="rgb/underglow",.h_set=rgb_settings_set};
    assert(zmk_rgb_underglow_init(NULL)==0);
}
static void activity(bool active) {
#if ORIGINAL
    assert(rgb_underglow_auto_state(&previous_state,active)==0);
#else
    assert(rgb_underglow_auto_state(active)==0);
#endif
}
int main(void) {
    saved=(struct rgb_underglow_state){.color={120,100,40},.animation_speed=3,.current_effect=2,.on=true};
    reboot(); assert(state.on && timer_running);
    uint32_t preset; assert(zmk_rgb_underglow_get_snapshot(&preset)==0);
    // A pending user save may execute after inactivity. It must retain the user choice.
    assert(zmk_rgb_underglow_select_effect(3)==0 && pending_save);
    activity(false); assert(!timer_running);
    flush();
#if ORIGINAL
    assert(!saved.on);
    reboot(); assert(!state.on && !timer_running);
    assert(zmk_rgb_underglow_select_effect(2)==0 && !timer_running);
    assert(zmk_rgb_underglow_apply_snapshot(preset)==0 && state.on && timer_running);
    puts("REPRODUCED: idle persists off; reboot stays dark; changing mode cannot restart it; loading an on preset does.");
#else
    assert(saved.on && saved.current_effect==3 && state.on && rgb_suspended);
    reboot(); assert(state.on && timer_running && !rgb_suspended);
    // Idle/wake never writes a transient off state and preserves explicit off.
    unsigned before=writes;
    activity(false); assert(rgb_suspended && state.on && !timer_running && !pending_save);
    activity(true); assert(!rgb_suspended && state.on && timer_running && !pending_save && writes==before);
    assert(zmk_rgb_underglow_off()==0); flush();
    assert(!saved.on); reboot(); assert(!state.on && !timer_running);
    activity(false); activity(true); assert(!state.on && !timer_running);
    assert(zmk_rgb_underglow_select_effect(5)==0 && !timer_running);
    assert(zmk_rgb_underglow_apply_snapshot(preset)==0 && state.on && timer_running);
    activity(false); assert(rgb_suspended && !timer_running);
    assert(zmk_rgb_underglow_apply_snapshot(preset)==0 && !rgb_suspended && timer_running);
    puts("PASS: actual startup/settings/idle code preserves on across idle+reboot, delayed saves, explicit off and preset wake.");
#endif
}
'''
names = ['rgb_settings_set', 'zmk_rgb_underglow_save_state_work',
         'zmk_rgb_underglow_init', 'zmk_rgb_underglow_save_state',
         'zmk_rgb_underglow_on', 'zmk_rgb_underglow_off',
         'zmk_rgb_underglow_get_snapshot', 'zmk_rgb_underglow_apply_snapshot',
         'zmk_rgb_underglow_select_effect', 'rgb_underglow_auto_state']
with tempfile.TemporaryDirectory(prefix='crisboard-startup-') as folder:
    temp = Path(folder)
    for name, text, original in [('baseline', baseline, 1), ('target', target, 0)]:
        enum = re.search(r'enum rgb_underglow_effect \{.*?\n\};', text, re.S)[0]
        struct = re.search(r'struct rgb_underglow_state \{.*?\n\};', text, re.S)[0]
        program = prefix + enum + '\n' + struct + settings
        program += '\n'.join(function(text, item) for item in names) + main
        source, binary = temp/(name+'.c'), temp/name
        source.write_text(program)
        subprocess.run(['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror',
            '-Wno-unused-parameter', '-Wno-unused-variable', '-Wno-unused-function',
            '-Wno-sign-compare', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
            '-no-pie', '-DORIGINAL='+str(original), '-I'+str(zmk/'app/include'),
            str(source), '-o', str(binary)], check=True)
        print(subprocess.check_output([str(binary)]).decode().strip())
