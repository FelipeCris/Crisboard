// SPDX-License-Identifier: MIT
#define DT_DRV_COMPAT zmk_behavior_crisboard_rgb_preset

#include <device.h>
#include <drivers/behavior.h>
#include <kernel.h>
#include <logging/log.h>
#include <settings/settings.h>
#include <stdio.h>
#include <string.h>
#include <zmk/ble.h>
#include <zmk/event_manager.h>
#include <zmk/events/layer_state_changed.h>
#include <zmk/keymap.h>
#include <zmk/rgb_underglow.h>
#include <zmk/crisboard_rgb_presets.h>
#if ZMK_BLE_IS_CENTRAL
#include <zmk/split/bluetooth/central.h>
#endif

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

static uint32_t presets[CRISBOARD_PRESET_COUNT];
static uint8_t valid_slots;
static int pending_slot = -1;
static uint32_t pending_position;
static int64_t pending_started;
static bool pending_can_save;
static bool pending_saved;
static struct k_work_delayable hold_work;

static int preset_settings_set(const char *name, size_t length,
                               settings_read_cb read_cb, void *cb_arg) {
    if (strlen(name) != 2 || name[0] != 'p' || name[1] < '0' || name[1] > '4') {
        return -ENOENT;
    }
    uint8_t slot = name[1] - '0';
    uint8_t record[8];
    if (length != sizeof(record)) {
        return -EINVAL;
    }
    int ret = read_cb(cb_arg, record, sizeof(record));
    if (ret < 0) {
        return ret;
    }
    if (ret != sizeof(record) || !crisboard_preset_decode(slot, record, 4, &presets[slot])) {
        return -EINVAL;
    }
    valid_slots |= BIT(slot);
    return 0;
}

static struct settings_handler preset_conf = {
    .name = "crisboard_rgb", .h_set = preset_settings_set,
};

static int save_preset(uint8_t slot) {
    uint32_t snapshot;
    int ret = zmk_rgb_underglow_get_snapshot(&snapshot);
    if (ret < 0) {
        return ret;
    }
    if ((valid_slots & BIT(slot)) && presets[slot] == snapshot) {
        return 0;
    }
    uint8_t record[8];
    char key[] = "crisboard_rgb/p0";
    key[sizeof(key) - 2] = '0' + slot;
    crisboard_preset_encode(slot, snapshot, record);
    ret = settings_save_one(key, record, sizeof(record));
    if (ret == 0) {
        presets[slot] = snapshot;
        valid_slots |= BIT(slot);
    }
    return ret;
}

static int load_preset(uint8_t slot) {
    if (!(valid_slots & BIT(slot))) {
        return 0;
    }
    struct zmk_behavior_binding binding = {
        .behavior_dev = "RGB_UG", .param1 = CRISBOARD_RGB_APPLY_CMD, .param2 = presets[slot],
    };
    struct zmk_behavior_binding_event event = {
        .layer = 2, .position = pending_position, .timestamp = k_uptime_get(),
    };
    // Use the native GLOBAL behavior transport with one absolute configuration,
    // so both halves load the central's preset even after independent restarts.
#if ZMK_BLE_IS_CENTRAL
    for (int i = 0; i < ZMK_BLE_SPLIT_PERIPHERAL_COUNT; i++) {
        int ret = zmk_split_bt_invoke_behavior(i, &binding, event, true);
        if (ret < 0) {
            LOG_WRN("Preset RGB delivery to peripheral failed: %d", ret);
        }
    }
#endif
    return behavior_keymap_binding_pressed(&binding, event);
}

static void save_held_preset(struct k_work *work) {
    if (pending_slot < 0 || pending_saved || !pending_can_save ||
        !zmk_keymap_layer_active(2)) {
        return;
    }
    if (k_uptime_get() - pending_started < CRISBOARD_PRESET_HOLD_MS) {
        k_work_reschedule(&hold_work,
            K_MSEC(CRISBOARD_PRESET_HOLD_MS - (k_uptime_get() - pending_started)));
        return;
    }
    int ret = save_preset(pending_slot);
    pending_saved = true;
    if (ret < 0) {
        LOG_ERR("Saving RGB preset failed: %d", ret);
    }
}

static int preset_pressed_sync(struct zmk_behavior_binding *binding,
                                struct zmk_behavior_binding_event event, bool fn_active) {
    if (binding->param1 >= CRISBOARD_PRESET_COUNT) {
        return -EINVAL;
    }
    if (pending_slot >= 0 || !fn_active) {
        return ZMK_BEHAVIOR_OPAQUE;
    }
    pending_slot = binding->param1;
    pending_position = event.position;
    pending_started = event.timestamp;
    pending_can_save = true;
    pending_saved = false;
    int64_t delay = MAX(0, CRISBOARD_PRESET_HOLD_MS - (k_uptime_get() - pending_started));
    k_work_reschedule(&hold_work, K_MSEC(delay));
    return ZMK_BEHAVIOR_OPAQUE;
}

static int preset_released_sync(struct zmk_behavior_binding *binding,
                                 struct zmk_behavior_binding_event event, bool fn_active) {
    if (pending_slot < 0 || event.position != pending_position) {
        return ZMK_BEHAVIOR_OPAQUE;
    }
    k_work_cancel_delayable(&hold_work);
    int ret = 0;
    if (!pending_saved) {
        if (pending_can_save && fn_active &&
            event.timestamp - pending_started >= CRISBOARD_PRESET_HOLD_MS) {
            ret = save_preset(pending_slot);
        } else {
            ret = load_preset(pending_slot);
        }
    }
    pending_slot = -1;
    return ret;
}

// Serialize preset state and NVS access on the system work queue. Split input
// callbacks have a small BLE stack; they only enqueue bounded event records.
struct preset_command {
    struct zmk_behavior_binding_event event;
    uint8_t slot;
    uint8_t kind; // 0 press, 1 release, 2 Fn deactivated
    bool fn_active;
};
K_MSGQ_DEFINE(preset_commands, sizeof(struct preset_command), 8, 4);

static void process_preset_commands(struct k_work *work) {
    struct preset_command command;
    while (k_msgq_get(&preset_commands, &command, K_NO_WAIT) == 0) {
        struct zmk_behavior_binding binding = {.param1 = command.slot};
        int ret = 0;
        if (command.kind == 0) {
            ret = preset_pressed_sync(&binding, command.event, command.fn_active);
        } else if (command.kind == 1) {
            ret = preset_released_sync(&binding, command.event, command.fn_active);
        } else if (pending_slot >= 0) {
            pending_can_save = false;
            k_work_cancel_delayable(&hold_work);
        }
        if (ret < 0) {
            LOG_ERR("RGB preset command failed: %d", ret);
        }
    }
}

K_WORK_DEFINE(preset_commands_work, process_preset_commands);

static int queue_preset_command(struct zmk_behavior_binding *binding,
                                 struct zmk_behavior_binding_event event, uint8_t kind) {
    if (binding->param1 >= CRISBOARD_PRESET_COUNT) {
        return -EINVAL;
    }
    struct preset_command command = {.event = event, .slot = binding->param1,
        .kind = kind, .fn_active = zmk_keymap_layer_active(2)};
    int ret = k_msgq_put(&preset_commands, &command, K_NO_WAIT);
    if (ret < 0) {
        LOG_ERR("RGB preset event queue full: %d", ret);
        return ret;
    }
    k_work_submit(&preset_commands_work);
    return ZMK_BEHAVIOR_OPAQUE;
}

static int preset_pressed(struct zmk_behavior_binding *binding,
                           struct zmk_behavior_binding_event event) {
    return queue_preset_command(binding, event, 0);
}

static int preset_released(struct zmk_behavior_binding *binding,
                            struct zmk_behavior_binding_event event) {
    return queue_preset_command(binding, event, 1);
}

static int preset_layer_listener(const zmk_event_t *event) {
    if (!zmk_keymap_layer_active(2)) {
        struct zmk_behavior_binding binding = {.param1 = 0};
        struct zmk_behavior_binding_event position = {.timestamp = k_uptime_get()};
        queue_preset_command(&binding, position, 2);
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(crisboard_presets, preset_layer_listener);
ZMK_SUBSCRIPTION(crisboard_presets, zmk_layer_state_changed);

static int preset_init(const struct device *device) {
    k_work_init_delayable(&hold_work, save_held_preset);
    settings_subsys_init();
    int ret = settings_register(&preset_conf);
    if (ret < 0) {
        return ret;
    }
    return settings_load_subtree("crisboard_rgb");
}

static const struct behavior_driver_api preset_api = {
    .locality = BEHAVIOR_LOCALITY_CENTRAL,
    .binding_pressed = preset_pressed,
    .binding_released = preset_released,
};

DEVICE_DT_INST_DEFINE(0, preset_init, NULL, NULL, NULL, APPLICATION,
                      CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &preset_api);
