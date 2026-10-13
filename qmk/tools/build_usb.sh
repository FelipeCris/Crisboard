#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
qmk_root="${1:?QMK checkout required}"
output="${2:?Output directory required}"
python3 "$repo_root/qmk/tools/verify_two_options.py"
test "$(git -C "$qmk_root" rev-parse HEAD)" = 0a3f7e48690bb2b7b008300a54554979a55be19a
mkdir -p "$output"
git -C "$qmk_root" submodule update --init --depth 1 lib/lufa lib/printf
cd "$qmk_root"
{
    git rev-parse HEAD
    git submodule status
    avr-gcc --version
    python3 --version
    pip freeze
} > "$output/toolchain.txt"
for side in left right; do
for variant in baseline optimized; do
    source="$repo_root/qmk/keyboards/crisboard"
    if [ "$variant" = baseline ]; then
        source="$repo_root/qmk/snapshots/2023-06/crisboard"
    fi
    cp -a "$source" keyboards/
    python3 "$repo_root/qmk/tools/reconstruct_baseline.py" --keyboard-root "$qmk_root/keyboards/crisboard" --side "$side"
    name="$side-$variant"
    make clean > "$output/$name-clean.log" 2>&1
    make crisboard:default -j2 2>&1 | tee "$output/$name-build.log"
    cp crisboard_default.hex "$output/$name.hex"
    cp .build/crisboard_default.elf "$output/$name.elf"
    avr-size -A .build/crisboard_default.elf > "$output/$name-size.txt"
    avr-nm -S --defined-only .build/crisboard_default.elf > "$output/$name-symbols.txt"
    python3 "$repo_root/qmk/tools/verify_usb_build.py" "$output/$name.hex" "$output/$name-symbols.txt" "$repo_root/qmk/recovered/keymap.json" > "$output/$name-verification.json"
    if [ "$variant" = baseline ]; then
        python3 "$repo_root/qmk/tools/reconstruct_baseline.py" --baseline-hex "$output/$name.hex" --side "$side"
    fi
done
done
python3 - "$output" <<'PY'
from pathlib import Path
import json, sys
output = Path(sys.argv[1])
report = {}
for side in ('left', 'right'):
    baseline = json.loads((output / f'{side}-baseline-verification.json').read_text())
    optimized = json.loads((output / f'{side}-optimized-verification.json').read_text())
    report[side] = {'baseline': baseline, 'optimized': optimized,
                    'bytes_saved': baseline['application_end'] - optimized['application_end']}
(output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
PY
