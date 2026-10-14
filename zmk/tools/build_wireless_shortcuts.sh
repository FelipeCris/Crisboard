#!/usr/bin/env bash
set -euo pipefail
side="${1:?left or right required}"
case "$side" in left|right) ;; *) exit 2 ;; esac
repo="$PWD/config-repo"
baseline="$PWD/config-baseline"
cp -a "$repo/config" "$baseline"
git -C "$repo" show '47a51bd5570211f12730fbfb5cf8910dedf5b8a2:config/boards/shields/Crisboard/crisboard.keymap' > "$baseline/boards/shields/Crisboard/crisboard.keymap"
git -C zmk apply --check "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply --check "$repo/zmk/patches/battery-voltage.patch"
git -C zmk apply "$repo/zmk/patches/battery-voltage.patch"
python3 "$repo/zmk/tools/test_battery_voltage.py" "$PWD/zmk"
for variant in baseline shortcuts; do
    configuration="$repo/config"
    if [ "$variant" = baseline ]; then configuration="$baseline"; fi
    west build -d "build-$variant" -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$configuration" -DSHIELD="crisboard_${side}"
    python3 "$repo/zmk/tools/stabilize_handles.py" "build-$variant"
    mkdir -p "results/$variant"
    for file in zmk.uf2 zmk.hex zmk.elf zmk.map zephyr.dts .config; do
        cp "build-$variant/zephyr/$file" "results/$variant/"
    done
done
git -C zmk diff > results/applied-display-change.patch
test "$(git -C zmk diff --name-only | wc -l)" = 4
