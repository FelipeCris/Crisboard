"""Run actual RGB rendering, layer synchronization and reconnect hook on a host compiler."""
from pathlib import Path
import colorsys
import json
import re
import subprocess
import sys
import tempfile

zmk = Path(sys.argv[1]).resolve()
baseline_rgb = Path(sys.argv[2]).resolve().read_text()
repo = Path(__file__).resolve().parents[2]
reference = json.loads((repo / 'zmk/inverse-borders-reference.json').read_text())
target_rgb = (zmk / 'app/src/rgb_underglow.c').read_text()


def function(text, name):
    match = re.search(r'(?m)^(?:static\s+)?[\w\s\*]+\b' + re.escape(name) + r'\([^;]*?\)\s*\{', text)
    assert match, name
    opening = text.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end]


palette_functions = ['hsb_scale_min_max', 'hsb_scale_zero_max', 'hsb_to_rgb',
    'zmk_rgb_underglow_effect_solid', 'zmk_rgb_underglow_effect_breathe',
    'zmk_rgb_underglow_effect_spectrum', 'zmk_rgb_underglow_effect_swirl',
    'zmk_rgb_underglow_effect_borders']
for name in palette_functions:
    assert function(baseline_rgb, name) == function(target_rgb, name), name

prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <zmk/crisboard_rgb_presets.h>
#include <zmk/crisboard_rgb_borders.h>
#define HUE_MAX 360
#define SAT_MAX 100
#define BRT_MAX 100
#define STRIP_NUM_PIXELS 34
struct zmk_led_hsb { uint16_t h; uint8_t s,b; };
struct led_rgb { uint8_t r,g,b; };
struct k_work { int unused; };
static struct led_rgb pixels[34];
static void *led_strip = (void *)1;
static bool crisboard_colemak_base = true;
static bool rgb_suspended;
static unsigned output_calls;
static int led_strip_update_rgb(void *strip, struct led_rgb *p, size_t n) {
    assert(strip == led_strip && p == pixels && n == 34); output_calls++; return 0;
}
static int zmk_rgb_underglow_save_state(void) { return 0; }
'''
main = r'''
int main(int argc, char **argv) {
    assert(argc == 2);
    if (!strcmp(argv[1], "legacy")) {
        for (unsigned mode=0;mode<5;mode++)
        for (unsigned h=0;h<=360;h+=30)
        for (unsigned s=0;s<=100;s+=50)
        for (unsigned b=0;b<=100;b+=50)
        for (unsigned speed=1;speed<=5;speed+=4)
        for (unsigned step=0;step<=2400;step+=600) {
            state=(struct rgb_underglow_state){.color={h,s,b},.animation_speed=speed,
                .current_effect=mode,.animation_step=step,.on=true};
            zmk_rgb_underglow_tick(NULL);
            assert(fwrite(pixels,sizeof(pixels),1,stdout)==1);
            assert(fwrite(&state.animation_step,sizeof(state.animation_step),1,stdout)==1);
        }
        assert(output_calls==5*13*3*3*2*5);
        return 0;
    }
#if TARGET_NEW
    assert(UNDERGLOW_EFFECT_SOLID==0 && UNDERGLOW_EFFECT_BREATHE==1 &&
        UNDERGLOW_EFFECT_SPECTRUM==2 && UNDERGLOW_EFFECT_SWIRL==3 &&
        UNDERGLOW_EFFECT_BORDERS==4 && UNDERGLOW_EFFECT_BORDERS_BREATHE==5 && UNDERGLOW_EFFECT_NUMBER==6);
    if (!strcmp(argv[1], "breathing")) {
        static const unsigned hues[]={0,59,60,120,179,180,240,300,359,360};
        static const unsigned brights[]={0,1,40,100};
        for (unsigned base=0;base<2;base++)
        for (unsigned hi=0;hi<10;hi++)
        for (unsigned s=0;s<=100;s+=50)
        for (unsigned bi=0;bi<4;bi++)
        for (unsigned step=0;step<=2400;step+=600) {
            state=(struct rgb_underglow_state){.color={hues[hi],s,brights[bi]},.animation_speed=5,
                .current_effect=UNDERGLOW_EFFECT_BORDERS_BREATHE,.animation_step=step,.on=true};
            assert(zmk_rgb_underglow_set_base_context(base)==0);
            zmk_rgb_underglow_tick(NULL);
            assert(state.animation_step==(step+50>2400?0:step+50));
            if (base==1) for(unsigned i=1;i<34;i++) assert(!memcmp(&pixels[0],&pixels[i],sizeof(pixels[0])));
            assert(fwrite(pixels,sizeof(pixels),1,stdout)==1);
        }
        return 0;
    }
    for (unsigned led=0;led<256;led++) {
        static const unsigned expected[]={ BORDER_LEDS };
        bool border=false;
        for (unsigned i=0;i<sizeof(expected)/sizeof(expected[0]);i++) border|=led==expected[i];
        assert(crisboard_rgb_is_border(led)==border);
    }
    for (unsigned mode=0;mode<6;mode++) {
        state.current_effect=mode;
        assert(zmk_rgb_underglow_calc_effect(1)==(mode+1)%6);
        assert(zmk_rgb_underglow_calc_effect(-1)==(mode+5)%6);
        assert(zmk_rgb_underglow_select_effect(mode)==0);
    }
    assert(zmk_rgb_underglow_select_effect(6)==-EINVAL && state.current_effect==5);
    assert(zmk_rgb_underglow_set_base_context(2)==-EINVAL);
    static const unsigned hues[]={0,59,60,120,179,180,240,300,359,360};
    static const unsigned brights[]={0,1,40,100};
    for (unsigned base=0;base<2;base++)
    for (unsigned hi=0;hi<10;hi++)
    for (unsigned s=0;s<=100;s+=50)
    for (unsigned bi=0;bi<4;bi++) {
        state=(struct rgb_underglow_state){.color={hues[hi],s,brights[bi]},.animation_speed=5,
            .current_effect=UNDERGLOW_EFFECT_BORDERS,.animation_step=123,.on=true};
        assert(zmk_rgb_underglow_set_base_context(base)==0);
        zmk_rgb_underglow_tick(NULL);
        assert(state.animation_step==123 && state.animation_speed==5);
        if (base==1) {
            struct led_rgb uniform[34]; memcpy(uniform,pixels,sizeof(uniform));
            zmk_rgb_underglow_effect_solid();
            assert(!memcmp(uniform,pixels,sizeof(uniform)));
        }
        assert(fwrite(pixels,sizeof(pixels),1,stdout)==1);
    }
    unsigned before=output_calls;
    rgb_suspended=true; state.on=true; zmk_rgb_underglow_tick(NULL);
    assert(output_calls==before);
    rgb_suspended=false; state.on=false; zmk_rgb_underglow_tick(NULL);
    assert(output_calls==before);
    return 0;
#else
    abort();
#endif
}
'''.replace('BORDER_LEDS', ','.join(map(str,reference['border_leds_per_half'])))

sync_stubs = r'''
#pragma once
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <zmk/crisboard_rgb_presets.h>
#define ZMK_BLE_SPLIT_PERIPHERAL_COUNT 1
#define ZMK_EV_EVENT_BUBBLE 0
#define ZMK_LISTENER(...)
#define ZMK_SUBSCRIPTION(...)
struct zmk_layer_state_changed { uint8_t layer; bool state; };
typedef struct zmk_layer_state_changed zmk_event_t;
static const struct zmk_layer_state_changed *as_zmk_layer_state_changed(const zmk_event_t *e) { return e; }
struct zmk_behavior_binding { const char *behavior_dev; uint32_t param1,param2; };
struct zmk_behavior_binding_event { int64_t timestamp; };
struct k_work { void (*handler)(struct k_work *); bool queued; };
#define K_WORK_DEFINE(n,f) struct k_work n={.handler=f}
static int k_work_submit(struct k_work *w) { w->queued=true; return 1; }
static bool qwerty;
static unsigned local_base=99, peripheral_base=99, packets;
static int64_t k_uptime_get(void) { return 42; }
static bool zmk_keymap_layer_active(uint8_t layer) { assert(layer==1); return qwerty; }
static int zmk_rgb_underglow_set_base_context(uint32_t b) { assert(b<=1); local_base=b; return 0; }
static int zmk_split_bt_invoke_behavior(uint8_t i, struct zmk_behavior_binding *b, struct zmk_behavior_binding_event e,bool pressed) {
    assert(i==0 && pressed && !strcmp(b->behavior_dev,"RGB_UG") && b->param1==129 && e.timestamp==42);
    peripheral_base=b->param2; packets++; return 0;
}
'''
sync_test = r'''
static void drain(void) { assert(crisboard_base_work.queued); crisboard_base_work.queued=false; crisboard_base_work.handler(&crisboard_base_work); }
int main(void) {
    struct zmk_layer_state_changed event={.layer=2,.state=true};
    assert(base_layer_listener(&event)==0 && !crisboard_base_work.queued && packets==0);
    event.layer=1; qwerty=true; base_layer_listener(&event); drain();
    assert(local_base==1 && peripheral_base==1 && packets==1);
    event.layer=2; event.state=false; base_layer_listener(&event); assert(!crisboard_base_work.queued);
    event.layer=1; qwerty=false; base_layer_listener(&event); drain();
    assert(local_base==0 && peripheral_base==0 && packets==2);
    // A reconnect queues fresh state, not the state when a previous event arrived.
    zmk_crisboard_rgb_sync_base(); qwerty=true; drain();
    assert(local_base==1 && peripheral_base==1 && packets==3);
    puts("PASS: actual base-sync module, Fn isolation, both-half context and fresh reconnect replay.");
}
'''

with tempfile.TemporaryDirectory(prefix='crisboard-border-tests-') as directory:
    temp = Path(directory)
    flags = ['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-parameter',
        '-Wno-unused-function','-Wno-unused-variable','-Wno-sign-compare',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',
        '-I'+str(temp),'-I'+str(zmk/'app/include')]

    def compile_run(name, program, args=(), extra_flags=()):
        source=temp/(name+'.c')
        binary=temp/name
        source.write_text(program)
        subprocess.run(flags+list(extra_flags)+[str(source),'-o',str(binary)],check=True)
        return subprocess.check_output([str(binary),*args])

    for minimum,maximum in [(0,100),(10,37)]:
        outputs={}
        for variant,text in [('baseline',baseline_rgb),('target',target_rgb)]:
            enum=re.search(r'enum rgb_underglow_effect \{.*?\n\};',text,re.S)[0]
            state_struct=re.search(r'struct rgb_underglow_state \{.*?\n\};',text,re.S)[0]
            functions=palette_functions+['zmk_rgb_underglow_set_base_context']
            if variant=='target':
                functions+=['zmk_rgb_underglow_effect_borders_breathe']
            functions+=['zmk_rgb_underglow_tick','zmk_rgb_underglow_calc_effect','zmk_rgb_underglow_select_effect']
            program=prefix+'\n'+enum+'\n'+state_struct+'\nstatic struct rgb_underglow_state state;\n'
            program+='\n'.join(function(text,n) for n in functions)+'\n'+main
            extra=[f'-DTARGET_NEW={int(variant=="target")}',f'-DCONFIG_ZMK_RGB_UNDERGLOW_BRT_MIN={minimum}',f'-DCONFIG_ZMK_RGB_UNDERGLOW_BRT_MAX={maximum}']
            outputs[variant]=compile_run(variant,program,['legacy'],extra)
            if variant=='target':
                borders=subprocess.check_output([str(temp/variant),'borders'])
        assert outputs['baseline']==outputs['target'], 'A legacy effect or timing changed'
        cursor=0
        for base in range(2):
            for hue in [0,59,60,120,179,180,240,300,359,360]:
                for saturation in [0,50,100]:
                    for brightness in [0,1,40,100]:
                        scaled=minimum+(maximum-minimum)*brightness//100
                        for led in range(34):
                            expected_hue=(hue+180)%360 if base==0 and led in reference['border_leds_per_half'] else hue%360
                            expected=[int(v*255) for v in colorsys.hsv_to_rgb(expected_hue/360,saturation/100,scaled/100)]
                            actual=list(borders[cursor:cursor+3]); cursor+=3
                            assert len(actual)==3 and all(abs(a-b)<=1 for a,b in zip(actual,expected)), (base,hue,saturation,brightness,led,actual,expected)
        assert cursor==len(borders)
        breathing=subprocess.check_output([str(temp/'target'),'breathing'])
        cursor=0
        for base in range(2):
            for hue in [0,59,60,120,179,180,240,300,359,360]:
                for saturation in [0,50,100]:
                    for brightness in [0,1,40,100]:
                        for step in range(0,2401,600):
                            center=(brightness*abs(step-1200)//1200)*maximum//100
                            border=minimum+(maximum-minimum)*brightness//100
                            for led in range(34):
                                inverse=base==0 and led in reference['border_leds_per_half']
                                expected_hue=(hue+180)%360 if inverse else hue%360
                                value=border if inverse else center
                                expected=[int(v*255) for v in colorsys.hsv_to_rgb(expected_hue/360,saturation/100,value/100)]
                                actual=list(breathing[cursor:cursor+3]); cursor+=3
                                assert len(actual)==3 and all(abs(a-b)<=1 for a,b in zip(actual,expected)), (base,hue,saturation,brightness,step,led,actual,expected)
        assert cursor==len(breathing)
    print('PASS: five installed RGB modes byte-identical; sixth mode keeps inverse borders fixed and breathes the center; QWERTY uniform, chosen brightness, cycle and timing.')

    (temp/'sync_stubs.h').write_text(sync_stubs)
    for name in ['drivers/behavior.h','kernel.h','zmk/ble.h','zmk/event_manager.h',
        'zmk/events/layer_state_changed.h','zmk/keymap.h','zmk/rgb_underglow.h','zmk/split/bluetooth/central.h']:
        path=temp/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('#include "sync_stubs.h"\n')
    module=zmk/'app/src/crisboard_rgb_base_sync.c'
    result=compile_run('sync','#include "sync_stubs.h"\n#include "'+str(module)+'"\n'+sync_test)
    print(result.decode().strip())

    central=(zmk/'app/src/split/bluetooth/central.c').read_text()
    discovery=function(central,'split_central_chrc_discovery_func')
    assert 'if (subscribed)' in discovery and discovery.count('zmk_crisboard_rgb_sync_base();')==1
    # Compile the actual discovery function: reconnection must wait for both handles.
    discovery_stubs=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#define IS_ENABLED(x) 1
#define LOG_DBG(...)
#define LOG_ERR(...)
#define BT_GATT_ITER_STOP 1
#define BT_GATT_ITER_CONTINUE 0
#define BT_GATT_DISCOVER_CHARACTERISTIC 1
#define BT_GATT_CCC_NOTIFY 1
#define ZMK_SPLIT_BT_CHAR_POSITION_STATE_UUID 1
#define ZMK_SPLIT_BT_CHAR_RUN_BEHAVIOR_UUID 2
struct bt_conn { int unused; };
struct bt_uuid { int value; };
#define BT_UUID_DECLARE_128(x) (&(struct bt_uuid){x})
struct bt_gatt_chrc { struct bt_uuid *uuid; };
struct bt_gatt_attr { unsigned handle; void *user_data; };
struct bt_gatt_discover_params { void *uuid; unsigned start_handle,end_handle,type; };
struct subscribe { void *disc_params,*notify; unsigned end_handle,value_handle,value; };
struct peripheral_slot { struct bt_gatt_discover_params discover_params,sub_discover_params; struct subscribe subscribe_params; unsigned run_behavior_handle; };
static struct peripheral_slot slot;
static bool available=true;
static unsigned replays;
static void *split_central_notify_func;
static struct peripheral_slot *peripheral_slot_for_conn(struct bt_conn *c) { return available?&slot:NULL; }
static int bt_uuid_cmp(const struct bt_uuid *a,const struct bt_uuid *b) { return a->value-b->value; }
static unsigned bt_gatt_attr_value_handle(const struct bt_gatt_attr *a) { return a->handle+1; }
static void split_central_subscribe(struct bt_conn *c) {}
static void zmk_crisboard_rgb_sync_base(void) { replays++; }
'''
    discovery_main=r'''
int main(void) {
    struct bt_uuid pos={1},run={2}; struct bt_gatt_chrc pc={&pos},rc={&run};
    struct bt_gatt_attr pa={10,&pc},ra={20,&rc}; struct bt_gatt_discover_params params={0};
    assert(split_central_chrc_discovery_func(NULL,NULL,&params)==1 && replays==0);
    assert(split_central_chrc_discovery_func(NULL,&pa,&params)==0 && replays==0);
    assert(split_central_chrc_discovery_func(NULL,&ra,&params)==1 && replays==1);
    slot=(struct peripheral_slot){0};
    assert(split_central_chrc_discovery_func(NULL,&ra,&params)==0 && replays==1);
    assert(split_central_chrc_discovery_func(NULL,&pa,&params)==1 && replays==2);
    available=false;
    assert(split_central_chrc_discovery_func(NULL,&pa,&params)==1 && replays==2);
    puts("PASS: actual BLE discovery hook replays base only after the peripheral behavior handle is ready.");
}
'''
    result=compile_run('discovery',discovery_stubs+discovery+discovery_main)
    print(result.decode().strip())
