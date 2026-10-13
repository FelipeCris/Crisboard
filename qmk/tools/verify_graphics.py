"""Compare every puppy frame and OLED font byte with the reproduced baseline.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import json
from pathlib import Path
import re
import sys
from verify_usb_build import read_hex

SIZES = {"font":1344,"sit":192,"walk":192,"run":192,"bark":192,"sneak":96}

def blobs(hex_path,symbols_path):
    memory=read_hex(hex_path)
    result={}
    for line in symbols_path.read_text(encoding="ascii").splitlines():
        parts=line.split()
        if len(parts)!=4: continue
        for name,size in SIZES.items():
            if re.fullmatch(name+r"(?:\..*)?",parts[3]) and int(parts[1],16)==size:
                if name in result: raise ValueError("Duplicate graphics symbol")
                offset=int(parts[0],16)
                result[name]=bytes(memory[offset+i] for i in range(size))
    if result.keys()!=SIZES.keys(): raise ValueError("Missing graphics symbol")
    return result

if __name__=="__main__":
    baseline=blobs(Path(sys.argv[1]),Path(sys.argv[2]))
    actual=blobs(Path(sys.argv[3]),Path(sys.argv[4]))
    if baseline!=actual: raise ValueError("OLED graphics differ from original")
    print(json.dumps({"font_bytes_unchanged":1344,"puppy_bytes_unchanged":864,"verified":True}))
