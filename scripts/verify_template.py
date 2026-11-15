#!/usr/bin/env python3
"""Stdlib-only check: does a GGUF's embedded chat template carry the
cache-reuse fix (guard `and reasoning_content` on the last_query_index
condition)? Exits 0 if the fix is present, 1 otherwise."""
import struct, sys

FMTS = {0:'<B',1:'<b',2:'<H',3:'<h',4:'<I',5:'<i',6:'<f',7:'<B',10:'<Q',11:'<q',12:'<d'}
SIZES = {0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}

def read_str(f):
    (n,) = struct.unpack('<Q', f.read(8))
    return f.read(n).decode('utf-8', errors='replace')

def read_val(f, t):
    if t == 8:
        return read_str(f)
    if t == 9:
        (et,) = struct.unpack('<I', f.read(4))
        (n,) = struct.unpack('<Q', f.read(8))
        return [read_val(f, et) for _ in range(n)]
    (v,) = struct.unpack(FMTS[t], f.read(SIZES[t]))
    return v

def main(path):
    with open(path, 'rb') as f:
        assert f.read(4) == b'GGUF', "not a GGUF file"
        f.read(4)  # version
        f.read(8)  # tensor count
        (nk,) = struct.unpack('<Q', f.read(8))
        tmpl = None
        for _ in range(nk):
            k = read_str(f)
            (t,) = struct.unpack('<I', f.read(4))
            v = read_val(f, t)
            if k == 'tokenizer.chat_template':
                tmpl = v
    if tmpl is None:
        print("FAIL: no tokenizer.chat_template in GGUF metadata")
        return 1
    for line in tmpl.splitlines():
        if 'last_query_index' in line and 'if' in line:
            print("condition line:", line.strip())
    if 'ns.last_query_index and reasoning_content' in tmpl:
        print("OK: embedded template carries the cache-reuse fix")
        return 0
    print("FAIL: embedded template does NOT carry the fix")
    return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
