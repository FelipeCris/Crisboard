#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
qmk_root="${1:?QMK checkout required}"
output="${2:?Output directory required}"
test "$(git -C "$qmk_root" rev-parse HEAD)" = 0a3f7e48690bb2b7b008300a54554979a55be19a
mkdir -p "$output"
git -C "$qmk_root" submodule update --init --depth 1 lib/lufa lib/printf
cp -a "$repo_root/qmk/keyboards/crisboard" "$qmk_root/keyboards/"
cd "$qmk_root"
{
    git rev-parse HEAD
    git submodule status
    avr-gcc --version
    python3 --version
    pip freeze
} > "$output/toolchain.txt"
for variant in baseline optimized; do
    cp "$repo_root/qmk/keyboards/crisboard/config.h" keyboards/crisboard/config.h
    lto=yes
    if [ "$variant" = baseline ]; then
        echo '#define ENABLE_RGB_MATRIX_CYCLE_SPIRAL' >> keyboards/crisboard/config.h
        lto=no
    fi
    make clean > "$output/$variant-clean.log" 2>&1
    make crisboard:default -j2 LTO_ENABLE="$lto" 2>&1 | tee "$output/$variant-build.log"
    cp crisboard_default.hex "$output/$variant.hex"
    cp .build/crisboard_default.elf "$output/$variant.elf"
    avr-size -A .build/crisboard_default.elf > "$output/$variant-size.txt"
    avr-nm -S --defined-only .build/crisboard_default.elf > "$output/$variant-symbols.txt"
    python3 "$repo_root/qmk/tools/verify_usb_build.py" "$output/$variant.hex" "$output/$variant-symbols.txt" "$repo_root/qmk/recovered/keymap.json" > "$output/$variant-verification.json"
done
python3 - "$output" <<'PY'
from pathlib import Path
import json, sys
output = Path(sys.argv[1])
baseline = json.loads((output / 'baseline-verification.json').read_text())
optimized = json.loads((output / 'optimized-verification.json').read_text())
report = {'baseline': baseline, 'optimized': optimized,
          'bytes_saved': baseline['application_end'] - optimized['application_end']}
(output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
PY
