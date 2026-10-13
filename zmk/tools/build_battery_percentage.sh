#!/usr/bin/env bash
set -euo pipefail
side="${1:?left or right required}"
case "$side" in left|right) ;; *) exit 2 ;; esac
repo="$PWD/config-repo"
baseline="$PWD/config-icon"
cp -a "$repo/config" "$baseline"
python3 - "$baseline" <<'PY'
from pathlib import Path
import sys
for path in Path(sys.argv[1]).rglob('crisboard_*.conf'):
    data = path.read_bytes().replace(b'\r\n', b'\n')
    data = data.replace(b'CONFIG_ZMK_WIDGET_BATTERY_STATUS=y\nCONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_PERCENTAGE=y',
                        b'# CONFIG_ZMK_WIDGET_BATTERY_STATUS=n')
    path.write_bytes(data)
PY
west build -d build-icon -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$baseline" -DSHIELD="crisboard_${side}"
git -C zmk apply --check "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply "$repo/zmk/patches/battery-percentage.patch"
west build -d build-percentage -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$repo/config" -DSHIELD="crisboard_${side}"
for variant in icon percentage; do
    mkdir -p "results/$variant"
    for file in zmk.uf2 zmk.hex zmk.elf zmk.map zephyr.dts .config; do
        if [ -f "build-$variant/zephyr/$file" ]; then
            cp "build-$variant/zephyr/$file" "results/$variant/"
        fi
    done
done
git -C zmk diff > results/applied-upstream-change.patch
test "$(git -C zmk diff --name-only | wc -l)" = 2
