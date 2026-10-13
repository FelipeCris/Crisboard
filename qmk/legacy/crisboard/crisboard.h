/* Copyright
 *   2021 solartempest
 *   2021 QMK
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include "quantum.h"

// clang-format off

#define LAYOUT( \
    L01, L02, L03, L04, L05, L06,              R06, R05, R04, R03, R02, R01, \
    L11, L12, L13, L14, L15, L16, L17,    R17, R16, R15, R14, R13, R12, R11, \
    L21, L22, L23, L24, L25, L26, L27,    R27, R26, R25, R24, R23, R22, R21, \
    L31, L32, L33, L34, L35, L36, L37,    R37, R36, R35, R34, R33, R32, R31, \
    L41, L42, L43, L44, L45, L46, L47,    R47, R46, R45, R44, R43, R42, R41 \
    ) \
    { \
        { L01, L02, L03, L04, L05, L06, KC_NO}, \
        { L11, L12, L13, L14, L15, L16, L17 }, \
        { L21, L22, L23, L24, L25, L26, L27 }, \
        { L31, L32, L33, L34, L35, L36, L37 }, \
        { L41, L42, L43, L44, L45, L46, L47 }, \
        { R01, R02, R03, R04, R05, R06, KC_NO }, \
        { R11, R12, R13, R14, R15, R16, R17 }, \
        { R21, R22, R23, R24, R25, R26, R27 }, \
        { R31, R32, R33, R34, R35, R36, R37 }, \
        { R41, R42, R43, R44, R45, R46, R47 }  \
    }


/*
#define LAYOUT( \
    LA1, LA2, LA3, LA4, LA5, LA6,              RA6, RA5, RA4, RA3, RA2, RA1, \
    LB1, LB2, LB3, LB4, LB5, LB6, LB7,    RB7, RB6, RB5, RB4, RB3, RB2, RB1, \
    LC1, LC2, LC3, LC4, LC5, LC6, LC7,    RC7, RC6, RC5, RC4, RC3, RC2, RC1, \
    LD1, LD2, LD3, LD4, LD5, LD6, LD7,    RD7, RD6, RD5, RD4, RD3, RD2, RD1, \
    LE1, LE2, LE3, LE4, LE5, LE6, LE7,    RE7, RE6, RE5, RE4, RE3, RE2, RE1 \
    ) \
    { \
        { LA1, LA2, LA3, LA4, LA5, LA6, KC_NO}, \
        { LB1, LB2, LB3, LB4, LB5, LB6, LB7 }, \
        { LC1, LC2, LC3, LC4, LC5, LC6, LC7 }, \
        { LD1, LD2, LD3, LD4, LD5, LD6, LD7 }, \
        { LE1, LE2, LE3, LE4, LE5, LE6, LE7 }, \
        { RA1, RA2, RA3, RA4, RA5, RA6, KC_NO }, \
        { RB1, RB2, RB3, RB4, RB5, RB6, RB7 }, \
        { RC1, RC2, RC3, RC4, RC5, RC6, RC7 }, \
        { RD1, RD2, RD3, RD4, RD5, RD6, RD7 }, \
        { RE1, RE2, RE3, RE4, RE5, RE6, RE7 }  \
    }



#define LAYOUT( \
    LA1,    LA2, LA3, LA4, LA5, LA6,      \
    LB1,    LB2, LB3, LB4, LB5, LB6, LB7, \
    LC1,    LC2, LC3, LC4, LC5, LC6, LC7, \
    LD1,    LD2, LD3, LD4, LD5, LD6, LD7, \
    LE1,    LE2, LE3, LE4, LE5, LE6, LE7, \
            RA6, RA5, RA4, RA3, RA2, RA1, \
    RB7,    RB6, RB5, RB4, RB3, RB2, RB1, \
    RC7,    RC6, RC5, RC4, RC3, RC2, RC1, \
    RD7,    RD6, RD5, RD4, RD3, RD2, RD1, \
    RE7,    RE6, RE5, RE4, RE3, RE2, RE1 \
    ) \
    { \
        { LA1, LA2, LA3, LA4, LA5, LA6, KC_NO}, \
        { LB1, LB2, LB3, LB4, LB5, LB6, LB7 }, \
        { LC1, LC2, LC3, LC4, LC5, LC6, LC7 }, \
        { LD1, LD2, LD3, LD4, LD5, LD6, LD7 }, \
        { LE1, LE2, LE3, LE4, LE5, LE6, LE7 }, \
        { RA1, RA2, RA3, RA4, RA5, RA6, KC_NO }, \
        { RB1, RB2, RB3, RB4, RB5, RB6, RB7 }, \
        { RC1, RC2, RC3, RC4, RC5, RC6, RC7 }, \
        { RD1, RD2, RD3, RD4, RD5, RD6, RD7 }, \
        { RE1, RE2, RE3, RE4, RE5, RE6, RE7 }  \
    }

    */

/*
#define LAYOUT( \
    LA1,    LA2, LA3, LA4, LA5, LA6,      \
    LB1,    LB2, LB3, LB4, LB5, LB6, LB7, \
    LC1,    LC2, LC3, LC4, LC5, LC6, LC7, \
    LD1,    LD2, LD3, LD4, LD5, LD6, LD7, \
    LE1,    LE2, LE3, LE4, LE5, LE6, LE7, \
            RA6, RA5, RA4, RA3, RA2, RA1, \
    RB7,    RB6, RB5, RB4, RB3, RB2, RB1, \
    RC7,    RC6, RC5, RC4, RC3, RC2, RC1, \
    RD7,    RD6, RD5, RD4, RD3, RD2, RD1, \
    RE7,    RE6, RE5, RE4, RE3, RE2, RE1 \
    ) \
    { \
        { LA1,   LB1, LC1, LD1, LE1}, \
        { LA2,   LB2, LC2, LD2, LE2}, \
        { LA3,   LB3, LC3, LD3, LE3}, \
        { LA4,   LB4, LC4, LD4, LE4}, \
        { LA5,   LB5, LC5, LD5, LE5}, \
        { LA6,   LB6, LC6, LD6, LE6}, \
        { KC_NO, LB7, LC7, LD7, LE7}, \
        { RA1,   RB1, RC1, RD1, RE1}, \
        { RA2,   RB2, RC2, RD2, RE2}, \
        { RA3,   RB3, RC3, RD3, RE3}, \
        { RA4,   RB4, RC4, RD4, RE4}, \
        { RA5,   RB5, RC5, RD5, RE5}, \
        { RA6,   RB6, RC6, RD6, RE6}, \
        { KC_NO, RB7, RC7, RD7, RE7}, \
    }

*/
//RGB LED Conversion macro from physical array to electric array (+146 to firmware size)
// clang-format on
