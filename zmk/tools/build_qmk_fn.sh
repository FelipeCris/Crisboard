#!/usr/bin/env bash
set -euo pipefail
side="${1:?left or right required}"
case "$side" in left|right) ;; *) exit 2 ;; esac
repo="$PWD/config-repo"
baseline="$PWD/config-baseline"
cp -a "$repo/config" "$baseline"
git -C "$repo" show '4a3246a1106c31b2798e2e9c0d6c03dfe6cda053:config/boards/shields/Crisboard/crisboard.keymap' > "$baseline/boards/shields/Crisboard/crisboard.keymap"
git -C zmk apply --check "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply "$repo/zmk/patches/battery-percentage.patch"
git -C zmk apply --check "$repo/zmk/patches/battery-voltage.patch"
git -C zmk apply "$repo/zmk/patches/battery-voltage.patch"
python3 "$repo/zmk/tools/test_battery_voltage.py" "$PWD/zmk"
west build -d build-baseline -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$baseline" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-baseline

git -C zmk apply --check "$repo/zmk/patches/qmk-fn-presets.patch"
git -C zmk apply "$repo/zmk/patches/qmk-fn-presets.patch"
cp "$repo/zmk/features/crisboard_rgb_presets.h" zmk/app/include/zmk/crisboard_rgb_presets.h
cp "$repo/zmk/features/behavior_crisboard_rgb_preset.c" zmk/app/src/behaviors/behavior_crisboard_rgb_preset.c
cp "$repo/zmk/features/crisboard-rgb-preset.yaml" 'zmk/app/dts/bindings/behaviors/zmk,behavior-crisboard-rgb-preset.yaml'
python3 "$repo/zmk/tools/test_qmk_fn.py" "$PWD/zmk"
west build -d build-qmk-fn -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$repo/config" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-qmk-fn
for variant in baseline qmk-fn; do
    mkdir -p "results/$variant"
    for file in zmk.uf2 zmk.hex zmk.elf zmk.map zephyr.dts .config; do
        cp "build-$variant/zephyr/$file" "results/$variant/"
    done
done
git -C zmk diff > results/applied-changes.patch
