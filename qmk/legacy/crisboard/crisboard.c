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

#include "crisboard.h"

#ifdef RGB_MATRIX_ENABLE

led_config_t g_led_config = { {
  // Key Matrix to LED Index 
  {   5,       4,  3,   2,  1,  0, NO_LED  },
  {   6,      7, 8,  9,   10,  11,  30  },
  {   17,      16, 15, 14,  13, 12,  31 },        
  {   18,      21, 22, 25,  26, 29,  32 },        
  {   19,      20, 23, 24,  27, 28,  33 },       

  {   39,     38, 37, 36, 35, 34, NO_LED },
  {   40,     41, 42, 43, 44, 45, 64 },
  {   51,     50, 49, 48, 47, 46, 65 },
  {   52,     55, 56, 59, 60, 63, 66 },
  {   53,     54, 57, 58, 61, 62, 67 }


}, {
  // LED Index to Physical Position

  
  {   86,   0 }, {   69,   0 }, {  51,   0 }, {  34,   0 }, {   17,   0 }, {    0,   0 },
  {    0,  16 }, {   17,  16 }, {  34,  16 }, {  51,  16 }, { 69,  16 }, { 86,  16 },  
  {   86,  32 }, {   69,  32 }, {  51,  32 }, {  34,  32 }, { 17,  32 }, {  0,  32 }, 
  {    0,  48 }, {    0,  64 }, {  17,  64 }, {  17,  48 }, { 34,  48 }, { 34,  64 },
  {   51,  64 }, {   51,  48 }, {  69,  48 }, {  69,  64 }, { 86,  64 }, { 86,  48 },
  {  103,  16 }, {  103,  32 }, { 103,  48 }, {  103,  64 },



  {  138,   0 }, {  155,   0 }, {  172,   0 }, {  189,   0 }, {  206,   0 }, { 224,   0 },
  {  224,  16 }, {  206,  16 }, {  189,  16 }, {  172,  16 }, {  155,  16 }, { 138,  16 }, 
  {  138,  32 }, {  155,  32 }, {  172,  32 }, {  189,  32 }, {  206,  32 }, { 224,  32 },
  {  224,  48 }, {  224,  64 }, {  206,  64 }, {  206,  48 }, {  189,  48 }, {  189,  64 },
  {  172,  64 }, {  172,  48 }, {  155,  48 }, {  155,  64 }, {  138,  64 }, {  138,  48 },

  {  120,  64 }, {  120,  48 }, {  120,  32 }, {  120,  16 }
  


}, {
  // LED Index to Flag
  1, 1, 1, 1, 1, 1, 
  1, 4, 4, 4, 4, 4, 2, 
  1, 4, 4, 4, 4, 4, 2, 
  1, 4, 4, 4, 4, 4, 2, 
  1, 4, 4, 4, 4, 4, 2, 

  1, 1, 1, 1, 1, 1,
  2, 4, 4, 4, 4, 4, 1,
  2, 4, 4, 4, 4, 4, 1,
  2, 4, 4, 4, 4, 4, 1,
  2, 4, 4, 4, 4, 4, 1

} };

#endif