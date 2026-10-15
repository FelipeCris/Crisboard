// SPDX-License-Identifier: MIT
#include <drivers/behavior.h>
#include <kernel.h>
#include <zmk/ble.h>
#include <zmk/crisboard_rgb_presets.h>
#include <zmk/event_manager.h>
#include <zmk/events/layer_state_changed.h>
#include <zmk/keymap.h>
#include <zmk/rgb_underglow.h>
#include <zmk/split/bluetooth/central.h>

static void sync_base_work(struct k_work *work) {
    // Layer 1 stays active under Fn (layer 2), so Fn cannot change the base.
    uint32_t base = zmk_keymap_layer_active(1) ? 1 : 0;
    zmk_rgb_underglow_set_base_context(base);
    struct zmk_behavior_binding binding = {
        .behavior_dev = "RGB_UG", .param1 = CRISBOARD_RGB_BASE_CMD, .param2 = base,
    };
    struct zmk_behavior_binding_event event = {.timestamp = k_uptime_get()};
    for (int i = 0; i < ZMK_BLE_SPLIT_PERIPHERAL_COUNT; i++) {
        zmk_split_bt_invoke_behavior(i, &binding, event, true);
    }
}

K_WORK_DEFINE(crisboard_base_work, sync_base_work);

void zmk_crisboard_rgb_sync_base(void) {
    k_work_submit(&crisboard_base_work);
}

static int base_layer_listener(const zmk_event_t *event) {
    const struct zmk_layer_state_changed *change = as_zmk_layer_state_changed(event);
    if (change && change->layer == 1) {
        zmk_crisboard_rgb_sync_base();
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(crisboard_rgb_base, base_layer_listener);
ZMK_SUBSCRIPTION(crisboard_rgb_base, zmk_layer_state_changed);
