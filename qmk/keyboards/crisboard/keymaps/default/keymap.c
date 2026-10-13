#include QMK_KEYBOARD_H
#include "rgb_presets.h"
//#include <led_matrix.h>

//uint8_t  arst=   led_matrix_get_val(void);

HSV hsv ;
HSV hsv2 ;

int coloroffset = 50;
int coloroffset2 = 127;

enum aero_layers {
    /* _M_XYZ = Mac Os, _W_XYZ = Win/Linux */
    
    _COLEMAK,
    _QWERTY,
    _LOWER

};

enum custom_keycodes {
    KC_QWERTY = SAFE_RANGE,
    KC_LOWER
};


const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
/*
 * QWERTY
 * ,-----------------------------------------.                    ,----------------------------------------.
 * | ESC  |   1  |   2  |   3  |   4  |   5  |                   |   6  |   7  |   8  |   9  |   0  |  DEL |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * | CAPS |   Q  |   W  |   E  |   R  |   T  |  |°  |    |  +*   |   Y  |   U  |   I  |   O  |   P  | BSPC |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * | Tab  |   A  |   S  |   D  |   F  |   G  |      |    | RALT  |   H  |   J  |   K  |   L  |   Ñ  |  .   |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * |LShift|  <>  |   Z  |   X  |   C  |   V  |  SPC |    | ENTER |   B  |   N  |   M  |   -  |  UP  |  '?  |
 * |-----------------------------------------|-------    --------|-----------------------------------------|
 * | LCTR |  FN  | WIN  | LALT |   ´  |  ,;  | HOME |    |  END  |  SPC |   {  |   }  | LEFT | DOWN | RIGHT|
 *  -------------------------------------------------    ---------------------------------------------------
 */

[_QWERTY] = LAYOUT(
  KC_ESC,    KC_1,                KC_2,        KC_3,     KC_4,    KC_5,                                                KC_6,     KC_7,    KC_8,    KC_9,      KC_0,     KC_DEL,
  KC_CAPS,   KC_Q,                KC_W,        KC_E,     KC_R,    KC_T,      KC_GRV,                       KC_RBRC,    KC_Y,     KC_U,    KC_I,    KC_O,      KC_P,     KC_BSPC,
  KC_TAB,    KC_A,                KC_S,        KC_D,     KC_F,    KC_G,      KC_NO,                        KC_ALGR,    KC_H,     KC_J,    KC_K,    KC_L,      KC_SCLN,  KC_LBRC,
  KC_LSFT,   KC_NONUS_BACKSLASH,  KC_Z,        KC_X,     KC_C,    KC_V,      KC_SPC,                       KC_ENT,     KC_B,     KC_N,    KC_M,    KC_SLSH,   KC_UP,    KC_MINUS,
  KC_LCTRL,  MO(_LOWER),          KC_LGUI,     KC_LALT,  KC_DOT, KC_COMM,    KC_HOME,                      KC_END,     KC_SPC,   KC_QUOT, KC_BSLS, KC_LEFT,   KC_DOWN,  KC_RIGHT 
),


/*
 * COLEMAK
 * ,-----------------------------------------.                    ,----------------------------------------.
 * | ESC  |   1  |   2  |   3  |   4  |   5  |                   |   6  |   7  |   8  |   9  |   0  |  DEL |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * | CAPS |   Q  |   W  |   F  |   P  |   G  |  |°  |    |  +*   |   J  |   L  |   U  |   Y  |   Ñ  | BSPC |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * | Tab  |   A  |   R  |   S  |   T  |   D  |      |    | RALT  |   H  |   N  |   E  |   I  |   O  |  ´   |
 * |------+------+------+------+------+------|-------    --------|------+------+------+------+------+------|
 * |LShift|  <>  |   Z  |   X  |   C  |   V  |  SPC |    | ENTER |   B  |   K  |   M  |   -  |  UP  |  '?  |
 * |-----------------------------------------|-------    --------|-----------------------------------------|
 * | LCTR |  FN  |  WIN | LALT |   ´  |  ,;  | HOME |    |  END  |  SPC |   {  |   }  | LEFT | DOWN | RIGHT|
 *  -------------------------------------------------    ---------------------------------------------------
 */

[_COLEMAK] = LAYOUT(
  KC_ESC,    KC_1,                KC_2,        KC_3,     KC_4,    KC_5,                                                KC_6,     KC_7,    KC_8,    KC_9,      KC_0,     KC_DEL,
  KC_CAPS,   KC_Q,                KC_W,        KC_F,     KC_P,    KC_G,      KC_GRV,                       KC_RBRC,    KC_J,     KC_L,    KC_U,    KC_Y,      KC_SCLN,  KC_BSPC,
  KC_TAB,    KC_A,                KC_R,        KC_S,     KC_T,    KC_D,      KC_NO,                        KC_ALGR,    KC_H,     KC_N,    KC_E,    KC_I,      KC_O,     KC_DOT,
  KC_LSFT,   KC_NONUS_BACKSLASH,  KC_Z,        KC_X,     KC_C,    KC_V,      KC_SPC,                       KC_ENT,     KC_B,     KC_K,    KC_M,    KC_SLSH,   KC_UP,    KC_MINUS,
  KC_LCTRL,  MO(_LOWER),          KC_LGUI,     KC_LALT,  KC_LBRC, KC_COMM,    KC_HOME,                      KC_END,     KC_SPC,   KC_QUOT, KC_BSLS, KC_LEFT,   KC_DOWN,  KC_RIGHT 
),

/*
 * FN
 * ,----------------------------------------------.                    ,-----------------------------------------------.
 * | rgbOn/Off |   F1 |   F2 |   F3 |   F4 |   F5 |                   |  F6  |  F7  |  F8  |  F9     |  F10     |  F11    |
 * |-----------+------+------+------+------+------|-------    --------|------+------+------+---------+----------+---------|
 * | ESC       |   Q  |   W  |   E  |   R  |   T  | qwerty|   |colemak|   -  | mute | play |   O     |   P      |  F12    |
 * |-----------+------+------+------+------+------|-------    --------|------+------+------+---------+----------+---------|
 * | Tab       |   A  |   S  |   D  |   F  |   G  |   '  |    |       |   H  |   J  |   K  |   L     |   ;      |  '      |
 * |-----------+------+------+------+------+------|-------    --------|------+------+------+---------+----------+---------|
 * |LShift     |   -  |   -  |   -  |   -  |   -  |prntscrn|  |       |   -  |   -  |   -  |   -     |  rgbmode | rgbspeed|
 * |----------------------------------------------|-------    --------|---------------------------------------------------|
 * | LCTR      |  F1  |  F2  |  F3  |  F4  |   F5 |   >  |    |       |  F6  |  F7  |  F8  |rgbbrillo|  rgbsat  | rgbcolor|
 *  ------------------------------------------------------    -------------------------------------------------------------
 */

[_LOWER] = LAYOUT(
  RGB_TOG,    KC_F1,               KC_F2,   KC_F3,    KC_F4,   KC_F5,                                                KC_F6,    KC_F7,   KC_F8,   KC_F9,     KC_F10,             KC_F11,
  RGB_VAD,    RGB_VAI,                KC_W,    KC_E,     KC_R,    KC_T,      DF(_QWERTY),                 DF(_COLEMAK), CB_RGB_PRESET_1,     CB_RGB_PRESET_2,    CB_RGB_PRESET_3,    KC_O,      KC_P,         KC_F12,
  RGB_MODE_FORWARD,     RGB_HUI,                KC_S,    KC_D,     KC_F,    KC_G,      KC_NO,                        XXXXXXX,     KC_H,     KC_J,    KC_K,    KC_L,      KC_SCLN,            KC_DOT,
  RGB_SAD,    RGB_SAI,  KC_Z,    KC_X,     KC_C,    KC_V,      KC_PSCR,                      KC_MUTE,      KC_B,     KC_N,    KC_NO,    RGB_SPD,   KC_VOLU,   RGB_SPI,
  KC_LCTRL,   KC_LGUI,             KC_NO,   KC_LALT,  KC_LBRC, KC_COMM,    KC_HOME,                      KC_END,      KC_MPLY,   KC_QUOT, KC_BSLS, KC_MPRV,   KC_VOLD,            KC_MNXT 
)

};

#ifdef OLED_ENABLE

oled_rotation_t oled_init_user(oled_rotation_t rotation) {
  if (!is_keyboard_master()) {
    return OLED_ROTATION_180;  // flips the display 180 degrees if offhand
  }
  else{
    return OLED_ROTATION_270;
  }
  return rotation;
}
/**/
static void render_logo(void) {
    static const char PROGMEM qmk_logo[] = {
        0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f, 0x90, 0x91, 0x92, 0x93, 0x94,
        0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4,
        0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0xd4,
        0};

    oled_write_P(qmk_logo, false);
}

/* 32 * 14 os logos 
static const char PROGMEM windows_logoup[] = {
        151,152,0
    };

static const char PROGMEM windows_logodown[] = {
        183,184,0
    };

static const char PROGMEM mac_logoup[] = {
        149,150,0
    }; 

static const char PROGMEM mac_logodown[] = {
        181,182,0
    };
*/



/* KEYBOARD PET START */

/* settings */
#    define MIN_WALK_SPEED      10
#    define MIN_RUN_SPEED       40

/* advanced settings */
#    define ANIM_FRAME_DURATION 200  // how long each frame lasts in ms
#    define ANIM_SIZE           96   // number of bytes in array. If you change sprites, minimize for adequate firmware size. max is 1024

/* timers */
uint32_t anim_timer = 0;
uint32_t anim_sleep = 0;

/* current frame */
uint8_t current_frame = 0;

/* status variables */
int   current_wpm = 0;
led_t led_usb_state;


bool isSneaking = false;
bool isJumping  = false;
bool showedJump = true;

/* logic */
static void render_luna(int LUNA_X, int LUNA_Y) {
    /* Sit */
    static const char PROGMEM sit[2][ANIM_SIZE] = {/* 'sit1', 32x22px */
                                                   {
                                                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x1c, 0x02, 0x05, 0x02, 0x24, 0x04, 0x04, 0x02, 0xa9, 0x1e, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x10, 0x08, 0x68, 0x10, 0x08, 0x04, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x06, 0x82, 0x7c, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x04, 0x0c, 0x10, 0x10, 0x20, 0x20, 0x20, 0x28, 0x3e, 0x1c, 0x20, 0x20, 0x3e, 0x0f, 0x11, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                   },

                                                   /* 'sit2', 32x22px */
                                                   {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x1c, 0x02, 0x05, 0x02, 0x24, 0x04, 0x04, 0x02, 0xa9, 0x1e, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x90, 0x08, 0x18, 0x60, 0x10, 0x08, 0x04, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x0e, 0x82, 0x7c, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x04, 0x0c, 0x10, 0x10, 0x20, 0x20, 0x20, 0x28, 0x3e, 0x1c, 0x20, 0x20, 0x3e, 0x0f, 0x11, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}};

    /* Walk */
    static const char PROGMEM walk[2][ANIM_SIZE] = {/* 'walk1', 32x22px */
                                                    {
                                                        0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x40, 0x20, 0x10, 0x90, 0x90, 0x90, 0xa0, 0xc0, 0x80, 0x80, 0x80, 0x70, 0x08, 0x14, 0x08, 0x90, 0x10, 0x10, 0x08, 0xa4, 0x78, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x08, 0xfc, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x18, 0xea, 0x10, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x1c, 0x20, 0x20, 0x3c, 0x0f, 0x11, 0x1f, 0x03, 0x06, 0x18, 0x20, 0x20, 0x3c, 0x0c, 0x12, 0x1e, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                    },

                                                    /* 'walk2', 32x22px */
                                                    {
                                                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x40, 0x20, 0x20, 0x20, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x10, 0x28, 0x10, 0x20, 0x20, 0x20, 0x10, 0x48, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f, 0x20, 0xf8, 0x02, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x10, 0x30, 0xd5, 0x20, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, 0x20, 0x30, 0x0c, 0x02, 0x05, 0x09, 0x12, 0x1e, 0x02, 0x1c, 0x14, 0x08, 0x10, 0x20, 0x2c, 0x32, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                    }};

    /* Run */
    static const char PROGMEM run[2][ANIM_SIZE] = {/* 'run1', 32x22px */
                                                   {
                                                       0x00, 0x00, 0x00, 0x00, 0xe0, 0x10, 0x08, 0x08, 0xc8, 0xb0, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x40, 0x40, 0x3c, 0x14, 0x04, 0x08, 0x90, 0x18, 0x04, 0x08, 0xb0, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0xc4, 0xa4, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xc8, 0x58, 0x28, 0x2a, 0x10, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0e, 0x09, 0x04, 0x04, 0x04, 0x04, 0x02, 0x03, 0x02, 0x01, 0x01, 0x02, 0x02, 0x04, 0x08, 0x10, 0x26, 0x2b, 0x32, 0x04, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                   },

                                                   /* 'run2', 32x22px */
                                                   {
                                                       0x00, 0x00, 0x00, 0xe0, 0x10, 0x10, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x80, 0x78, 0x28, 0x08, 0x10, 0x20, 0x30, 0x08, 0x10, 0x20, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x04, 0x08, 0x10, 0x11, 0xf9, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x10, 0xb0, 0x50, 0x55, 0x20, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x0c, 0x10, 0x20, 0x28, 0x37, 0x02, 0x1e, 0x20, 0x20, 0x18, 0x0c, 0x14, 0x1e, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                   }};

    /* Bark */
    static const char PROGMEM bark[2][ANIM_SIZE] = {/* 'bark1', 32x22px */
                                                    {
                                                        0x00, 0xc0, 0x20, 0x10, 0xd0, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x40, 0x3c, 0x14, 0x04, 0x08, 0x90, 0x18, 0x04, 0x08, 0xb0, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x04, 0x08, 0x10, 0x11, 0xf9, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xc8, 0x48, 0x28, 0x2a, 0x10, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x0c, 0x10, 0x20, 0x28, 0x37, 0x02, 0x02, 0x04, 0x08, 0x10, 0x26, 0x2b, 0x32, 0x04, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                    },

                                                    /* 'bark2', 32x22px */
                                                    {
                                                        0x00, 0xe0, 0x10, 0x10, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x40, 0x40, 0x2c, 0x14, 0x04, 0x08, 0x90, 0x18, 0x04, 0x08, 0xb0, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x04, 0x08, 0x10, 0x11, 0xf9, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xc0, 0x48, 0x28, 0x2a, 0x10, 0x0f, 0x20, 0x4a, 0x09, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x0c, 0x10, 0x20, 0x28, 0x37, 0x02, 0x02, 0x04, 0x08, 0x10, 0x26, 0x2b, 0x32, 0x04, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                    }};

    /* Sneak */
    static const char PROGMEM sneak[] = {/* 'sneak1', 32x22px */
                                                                                                              0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x40, 0x40, 0x40, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x40, 0x40, 0x80, 0x00, 0x80, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1e, 0x21, 0xf0, 0x04, 0x02, 0x02, 0x02, 0x02, 0x03, 0x02, 0x02, 0x04, 0x04, 0x04, 0x03, 0x01, 0x00, 0x00, 0x09, 0x01, 0x80, 0x80, 0xab, 0x04, 0xf8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x1c, 0x20, 0x20, 0x3c, 0x0f, 0x11, 0x1f, 0x02, 0x06, 0x18, 0x20, 0x20, 0x38, 0x08, 0x10, 0x18, 0x04, 0x04, 0x02, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00,
                                    

                                                     /* 'sneak2', 32x22px 
                                                     {
                                                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x40, 0x40, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0xa0, 0x20, 0x40, 0x80, 0xc0, 0x20, 0x40, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3e, 0x41, 0xf0, 0x04, 0x02, 0x02, 0x02, 0x03, 0x02, 0x02, 0x02, 0x04, 0x04, 0x02, 0x01, 0x00, 0x00, 0x00, 0x04, 0x00, 0x40, 0x40, 0x55, 0x82, 0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, 0x20, 0x30, 0x0c, 0x02, 0x05, 0x09, 0x12, 0x1e, 0x04, 0x18, 0x10, 0x08, 0x10, 0x20, 0x28, 0x34, 0x06, 0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                     }*/};

    
    /* animation */
    
    void animate_luna(void) {
        /* jump */
        if (isJumping || !showedJump) {
            /* clear */
            oled_set_cursor(LUNA_X, LUNA_Y + 2);
            oled_write("     ", false);

            oled_set_cursor(LUNA_X, LUNA_Y - 1);

            showedJump = true;
        } else {
            /* clear */
            oled_set_cursor(LUNA_X, LUNA_Y - 1);
            oled_write("     ", false);

            oled_set_cursor(LUNA_X, LUNA_Y);
        }

        /* switch frame */
        current_frame = (current_frame + 1) % 2;

        /* current status */
        if (led_usb_state.caps_lock) {
            oled_write_raw_P(bark[abs(1 - current_frame)], ANIM_SIZE);

        } else if (isSneaking) {
            oled_write_raw_P(sneak, ANIM_SIZE);

        } else if (current_wpm <= MIN_WALK_SPEED) {
            oled_write_raw_P(sit[abs(1 - current_frame)], ANIM_SIZE);

        } else if (current_wpm <= MIN_RUN_SPEED) {
            oled_write_raw_P(walk[abs(1 - current_frame)], ANIM_SIZE);

        } else {
            oled_write_raw_P(run[abs(1 - current_frame)], ANIM_SIZE);
        }
    }

    /* animation timer */
    if (timer_elapsed32(anim_timer) > ANIM_FRAME_DURATION) {
        anim_timer = timer_read32();
        animate_luna();
    }

    /* this fixes the screen on and off bug */
    if (current_wpm > 0) {
        oled_on();
        anim_sleep = timer_read32();
    } else if (timer_elapsed32(anim_sleep) > OLED_TIMEOUT) {
        oled_off();
    }
}

/* KEYBOARD PET END */






static void print_logo_narrow(void) {
    render_logo();
}

static void print_status_narrow(void) {
    /* Print current mode 
    oled_set_cursor(2, 0);
    if (keymap_config.swap_lctl_lgui) {
        oled_write_P(mac_logoup, false);
        oled_set_cursor(2, 1);
        oled_write_P(mac_logodown, false);
    } else {
        oled_write_P(windows_logoup, false);
        oled_set_cursor(2, 1);
        oled_write_P(windows_logodown, false);
    }
    */

    oled_set_cursor(0, 1);
    oled_write_ln_P(PSTR("*****"), true);

    oled_set_cursor(0, 3);

    switch (get_highest_layer(default_layer_state)) {
        case _QWERTY:
            oled_write_ln_P(PSTR("QWRTY"), false);
            break;
        case _COLEMAK:
            oled_write_ln_P(PSTR("CLMK "), false);
            break;
        default:
            oled_write_P(PSTR("Undef"), false);
    }

    oled_set_cursor(0, 5);

    /* Print current layer */
    //oled_write("LAYER", false);


    switch (get_highest_layer(layer_state)) {
        case _COLEMAK:
            oled_write_P(PSTR(" Clmk\n"), false);
            break;
        case _QWERTY:
            oled_write_P(PSTR("Base\n"), false);
            break;
        case _LOWER:
            oled_write_P(PSTR("Lower"), false);
            break;
        default:
            oled_write_ln_P(PSTR(" Undef"), false);
    }

    /* caps lock */
    oled_set_cursor(0, 8);
    oled_write("CPSLK", led_usb_state.caps_lock);

    /* KEYBOARD PET RENDER START */

    render_luna(0, 13);

    /* KEYBOARD PET RENDER END */

    uint8_t n = get_current_wpm();
    char    wpm_str[5];
    oled_set_cursor(0, 11);
    wpm_str[4] = '\0';
    wpm_str[3] = '0' + n % 10;
    wpm_str[2] = '0' + (n /= 10) % 10;
    wpm_str[1] = '0' + n / 10;
    wpm_str[0] = ' ';
    oled_write(wpm_str, false);



}


bool oled_task_user(void) {
    /* KEYBOARD PET VARIABLES START */

    current_wpm   = get_current_wpm();
    led_usb_state = host_keyboard_led_state();

    /* KEYBOARD PET VARIABLES END */

    if (is_keyboard_master()) {
        print_status_narrow();
    } else {
        print_logo_narrow();
    }
    return false;
}
#endif



bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (!crisboard_process_rgb_presets(keycode, record)) {
        return false;
    }
    switch (keycode) {
        case KC_QWERTY:
            if (record->event.pressed) {
                set_single_persistent_default_layer(_QWERTY);
            }
            return false;
        case KC_LOWER:
            if (record->event.pressed) {
                set_single_persistent_default_layer(_LOWER);
            }
            return false;
        case KC_COPY:
            if (record->event.pressed) {
                register_mods(mod_config(MOD_LCTL));
                register_code(KC_C);
            } else {
                unregister_mods(mod_config(MOD_LCTL));
                unregister_code(KC_C);
            }
            return false;
        case KC_PASTE:
            if (record->event.pressed) {
                register_mods(mod_config(MOD_LCTL));
                register_code(KC_V);
            } else {
                unregister_mods(mod_config(MOD_LCTL));
                unregister_code(KC_V);
            }
            return false;
        case KC_CUT:
            if (record->event.pressed) {
                register_mods(mod_config(MOD_LCTL));
                register_code(KC_X);
            } else {
                unregister_mods(mod_config(MOD_LCTL));
                unregister_code(KC_X);
            }
            return false;
            break;
        case KC_UNDO:
            if (record->event.pressed) {
                register_mods(mod_config(MOD_LCTL));
                register_code(KC_Z);
            } else {
                unregister_mods(mod_config(MOD_LCTL));
                unregister_code(KC_Z);
            }
            return false;

        /* KEYBOARD PET STATUS START */

        case KC_LCTL:
        case KC_RCTL:
            if (record->event.pressed) {
                isSneaking = true;
            } else {
                isSneaking = false;
            }
            break;
        case KC_SPC:
            if (record->event.pressed) {
                isJumping  = true;
                showedJump = false;
            } else {
                isJumping = false;
            }
            break;

            /* KEYBOARD PET STATUS END */
    }
    return true;
}



void matrix_scan_user(void) {
    crisboard_rgb_presets_scan();
}

void set_color_split(uint8_t key_code, uint8_t r, uint8_t g, uint8_t b) {
    // When using defines for MASTER_LEFT and MASTER_RIGHT, is_keyboard_left()
    // will be inaccurate. For example, (is_keyboard_left() &&
    // !is_keyboard_master()) can NEVER be true.
#ifdef MASTER_LEFT
    bool is_left = true;
#endif
#ifdef MASTER_RIGHT
    bool is_left = false;
#endif

    bool left_is_master = (is_keyboard_master() && is_left) || (!is_keyboard_master() && !is_left);

    // Note on constants: 23 is the number of LEDs on each side (24) minus 1.
    // 27 is the number of LEDs that the Corne normally has with six columns.

    // Rule #1: you must set the LED based on what the master's range is. So if
    // the USB cable is in the left half, then the range is 0-23, otherwise it's
    // 27-50.

    // Rule #2: each half of the keyboard can only set its own LEDs, it's just
    // that the codes change according to Rule #1.

    // Rule #2
    if ((is_left && key_code >= 34) || (!is_left && key_code < 34)) {
        return;
    }

    // Rule #1
    if (left_is_master && key_code >= 34)
        key_code -= 34;
    else if (!left_is_master && key_code < 34)
        key_code += 34;
    rgb_matrix_set_color(key_code, r, g, b);
}

static void set_color_keys_range(int startKey, int endKey, RGB rgb) {
    for (int i = startKey; i <= endKey; i++) {
        set_color_split(i, rgb.r, rgb.g, rgb.b);
    }
}



void rgb_matrix_indicators_user(void) {

    switch (get_highest_layer(layer_state)) {
        case _QWERTY:
            //rgb_matrix_set_color_all(0, 0, 255); //Light up all the keys in blue
            break;
        case _COLEMAK:
            
            break;
        case _LOWER:
            //rgb_matrix_set_color(index, red, green, blue); >> this is the template
            hsv = rgb_matrix_get_hsv();
            hsv.h = (hsv.h+coloroffset)%255;
            RGB   rgb = hsv_to_rgb(hsv);
            //rgb_matrix_set_color_all(rgb.r, rgb.g, rgb.b); // rest of keys
            int ranges1[] = {28, 33, 62, 67};

            for (int i = 0; i < sizeof(ranges1) / sizeof(ranges1[0]); i += 2) {
                set_color_keys_range(ranges1[i], ranges1[i+1], rgb);
            }

        /*
            set_color_split(28, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(29, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(30, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(31, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(32, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(33, rgb.r, rgb.g, rgb.b); // rest of keys
            


            set_color_split(63, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(62, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(64, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(65, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(66, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(67, rgb.r, rgb.g, rgb.b); // rest of keys
        */

            break;
    }



    switch (get_highest_layer(default_layer_state)) {
        case _QWERTY:
            break;
        case _COLEMAK:

            hsv2 = rgb_matrix_get_hsv();
            hsv2.h = (hsv2.h+coloroffset2)%255;
            RGB   rgb = hsv_to_rgb(hsv2);
            

            //Rangos de teclas por pares, desde la tecla inicial a la tecla final, 0-6, 17-20, etc
            int ranges2[] = {0, 6, 17, 20, 23, 24, 27, 28, 32, 33, 34, 40, 51, 54, 57, 58, 61, 62, 66, 67};

            for (int i = 0; i < sizeof(ranges2) / sizeof(ranges2[0]); i += 2) {
                set_color_keys_range(ranges2[i], ranges2[i+1], rgb);
            }

/*            
            set_color_split(0, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(1, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(2, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(3, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(4, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(5, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(6, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(17, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(18, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(19, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(20, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(23, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(24, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(27, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(28, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(32, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(33, rgb.r, rgb.g, rgb.b); // rest of keys
           
            set_color_split(34, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(35, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(36, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(37, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(38, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(39, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(40, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(51, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(52, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(53, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(54, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(57, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(58, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(61, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(62, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(66, rgb.r, rgb.g, rgb.b); // rest of keys
            set_color_split(67, rgb.r, rgb.g, rgb.b); // rest of keys
         */   

            


            
            break;
        default:
           break;
    }

/*
    if (host_keyboard_led_state().caps_lock)
    {

      set_color_split(34,70, 150, 150);
      set_color_split(45,70, 150, 150);     
    }*/

}