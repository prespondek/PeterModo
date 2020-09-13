# python
# Python Lightwave Object (.lwo) Utility

# This library provides functions for reading and writing lwo files
# AIFC was used as a template

from chunk import Chunk
import __builtin__

import struct
import __builtin__

__all__ = ["Error","open","openfp"]

class Error(Exception):
    pass

def _read_long(file):
    try:
        return struct.unpack('>l', file.read(4))[0]
    except struct.error:
        raise EOFError

def _read_ulong(file):
    try:
        return struct.unpack('>L', file.read(4))[0]
    except struct.error:
        raise EOFError

def _read_short(file):
    try:
        return struct.unpack('>h', file.read(2))[0]
    except struct.error:
        raise EOFError

def _read_ushort(file):
    try:
        return struct.unpack('>H', file.read(2))[0]
    except struct.error:
        raise EOFError

def _read_astring(file,length):
    strings = []
    while length > 0:
        string = _read_string(file)
        strings.append(string)
        length = length - (len(string) + 1)
    return strings

def _read_avec(file,length):
    vectors = []
    while length > 0:
        vec = _read_vec(file)
        vectors.append(vec)
        length -= 12
    return vectors

def _read_string(file):
    string = ''
    while 1:
        char = file.read(1)
        if char == '\x00':
            break
        string += char
    return string
    

_HUGE_VAL = 1.79769313486231e+308 # See <limits.h>

def _read_float(file):
    try:
        return struct.unpack('>f', file.read(4))[0]
    except struct.error:
        raise EOFError

def _read_vec(file):
    return (_read_float(file),_read_float(file),_read_float(file))
    
def _write_short(f, x):
    f.write(struct.pack('>h', x))

def _write_long(f, x):
    f.write(struct.pack('>L', x))

def _write_string(f, s):
    if len(s) > 255:
        raise ValueError("string exceeds maximum pstring length")
    f.write(chr(len(s)))
    f.write(s)
    if len(s) & 1 == 0:
        f.write(chr(0))

def _write_float(f, x):
    import math
    if x < 0:
        sign = 0x8000
        x = x * -1
    else:
        sign = 0
    if x == 0:
        expon = 0
        himant = 0
        lomant = 0
    else:
        fmant, expon = math.frexp(x)
        if expon > 16384 or fmant >= 1:     # Infinity or NaN
            expon = sign|0x7FFF
            himant = 0
            lomant = 0
        else:                   # Finite
            expon = expon + 16382
            if expon < 0:           # denormalized
                fmant = math.ldexp(fmant, expon)
                expon = 0
            expon = expon | sign
            fmant = math.ldexp(fmant, 32)
            fsmant = math.floor(fmant)
            himant = long(fsmant)
            fmant = math.ldexp(fmant - fsmant, 32)
            fsmant = math.floor(fmant)
            lomant = long(fsmant)
    _write_short(f, expon)
    _write_long(f, himant)
    _write_long(f, lomant)

class lwo_read:
    def __init__(self, f):
        if type(f) == type(''):
            f = __builtin__.open(f, 'rb')
        # else, assume it is an open file object already
        self.initfp(f)
    def initfp(self, file):
        self._file = file
        chunk = Chunk(file)
        if chunk.getname() != 'FORM':
            raise Error, 'file does not start with FORM id'
        formdata = chunk.read(4)
        if not formdata == 'LWO2':
            raise Error, 'not an LWO2 file'
        while 1:
            try:
                chunk = Chunk(self._file)
            except EOFError:
                break
            chunkname = chunk.getname()
            print(chunkname)
            if chunkname == 'TAGS':
                self._tags = _read_astring(chunk,chunk.getsize())
                print(self._tags)
            if chunkname == 'LAYR':
                print (_read_ushort(chunk))
                print (_read_ushort(chunk))
                print (_read_vec(chunk))
                print (_read_string(chunk))
                if chunk.tell() < chunk.getsize():
                    print (_read_ushort(chunk))
            if chunkname == 'PNTS':
                print (_read_avec(chunk,chunk.getsize()))
            chunk.skip()     

def open(f, mode=None):
    if mode is None:
        if hasattr(f, 'mode'):
            mode = f.mode
        else:
            mode = 'rb'
    if mode in ('r', 'rb'):
        return lwo_read(f)
    elif mode in ('w', 'wb'):
        return lwo_write(f)
    else:
        raise Error, "mode must be 'r', 'rb', 'w', or 'wb'"

if __name__ == '__main__':
    import sys
    if not sys.argv[1:]:
        sys.argv.append('test.lwo')
    fn = sys.argv[1]
    f = open(fn, 'r')
    if sys.argv[2:]:
        gn = sys.argv[2]
        print "Writing", gn
        g = open(gn, 'w')
        g.close()
        f.close()
        print "Done."
