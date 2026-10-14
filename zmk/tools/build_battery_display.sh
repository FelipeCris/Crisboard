#!/usr/bin/env bash
set -euo pipefail
side="${1:?left or right required}"
case "$side" in left|right) ;; *) exit 2 ;; esac
repo="$PWD/config-repo"
baseline="$PWD/config-percentage"
cp -a "$repo/config" "$baseline"
python3 - "$baseline" <<'PY'
from pathlib import Path
import sys
for path in Path(sys.argv[1]).rglob('crisboard_*.conf'):
    data = path.read_bytes().replace(b'\r\n', b'\n')
    data = data.replace(b'CONFIG_ZMK_WIDGET_BATTERY_STATUS_SHOW_VOLTAGE=y\n', b'')
    path.write_bytes(data)
PY
git -C zmk apply --check "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply "$repo/zmk/patches/battery-percentage.patch"
west build -d build-percentage -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$baseline" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-percentage
git -C zmk apply --check "$repo/zmk/patches/battery-voltage.patch"
git -C zmk apply "$repo/zmk/patches/battery-voltage.patch"
python3 "$repo/zmk/tools/test_battery_voltage.py" "$PWD/zmk"
west build -d build-voltage -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$repo/config" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-voltage
for variant in percentage voltage; do
    mkdir -p "results/$variant"
    for file in zmk.uf2 zmk.hex zmk.elf zmk.map zephyr.dts .config; do
        cp "build-$variant/zephyr/$file" "results/$variant/"
    done
done
git -C zmk diff > results/applied-display-change.patch
test "$(git -C zmk diff --name-only | wc -l)" = 4
