#!/usr/bin/env bash
set -euo pipefail
side="${1:?left or right required}"
case "$side" in left|right) ;; *) exit 2 ;; esac
repo="$PWD/config-repo"
installed=33dfebf65ee3ffa68ee063685bca3a2b4473ced9
for patch in battery-percentage battery-voltage qmk-fn-presets; do
    git -C zmk apply --check "$repo/zmk/patches/$patch.patch"
    git -C zmk apply "$repo/zmk/patches/$patch.patch"
done
python3 "$repo/zmk/tools/prepare_handle_generator.py" "$PWD/zephyr"
git -C zephyr diff > results/handle-generator-order.patch
git -C "$repo" show "$installed:zmk/patches/inverse-borders.patch" > results/installed-inverse-borders.patch
git -C zmk apply --check "$PWD/results/installed-inverse-borders.patch"
git -C zmk apply "$PWD/results/installed-inverse-borders.patch"
for file in crisboard_rgb_presets.h crisboard_rgb_borders.h behavior_crisboard_rgb_preset.c crisboard_rgb_base_sync.c crisboard-rgb-preset.yaml; do
    case "$file" in
        crisboard_rgb_base_sync.c) target="zmk/app/src/$file" ;;
        *.h) target="zmk/app/include/zmk/$file" ;;
        *.c) target="zmk/app/src/behaviors/$file" ;;
        *.yaml) target='zmk/app/dts/bindings/behaviors/zmk,behavior-crisboard-rgb-preset.yaml' ;;
    esac
    git -C "$repo" show "$installed:zmk/features/$file" > "$target"
done
python3 "$repo/zmk/tools/test_battery_voltage.py" "$PWD/zmk"
cp zmk/app/src/rgb_underglow.c results/baseline-rgb.c
west build -d build-baseline -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$repo/config" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-baseline

for patch in breathing-borders rgb-idle-persistence; do
    git -C zmk apply --check "$repo/zmk/patches/$patch.patch"
    git -C zmk apply "$repo/zmk/patches/$patch.patch"
done
cp "$repo/zmk/features/crisboard_rgb_presets.h" zmk/app/include/zmk/
cp "$repo/zmk/features/crisboard_rgb_borders.h" zmk/app/include/zmk/
cp "$repo/zmk/features/behavior_crisboard_rgb_preset.c" zmk/app/src/behaviors/
cp "$repo/zmk/features/crisboard_rgb_base_sync.c" zmk/app/src/
python3 "$repo/zmk/tools/test_qmk_fn.py" "$PWD/zmk"
python3 "$repo/zmk/tools/test_rgb_startup.py" "$PWD/zmk" "$PWD/results/baseline-rgb.c"
python3 "$repo/zmk/tools/test_inverse_borders.py" "$PWD/zmk" "$PWD/results/baseline-rgb.c"
west build -d build-inverse-borders -s zmk/app -b nice_nano_v2 -- -DZMK_CONFIG="$repo/config" -DSHIELD="crisboard_${side}"
python3 "$repo/zmk/tools/stabilize_handles.py" build-inverse-borders
for variant in baseline inverse-borders; do
    mkdir -p "results/$variant"
    for file in zmk.uf2 zmk.hex zmk.elf zmk.map zephyr.dts .config; do
        cp "build-$variant/zephyr/$file" "results/$variant/"
    done
done
git -C zmk diff > results/applied-changes.patch
