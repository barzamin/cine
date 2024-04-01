import IPython
import struct
from memory import DOLMemory
from util import hexdump
import logging

# logging.basicConfig(level=logging.DEBUG)

mem = DOLMemory()

a_StaticPlayer_0 = 0x80453080
a_StaticPlayer_0_p_Fighter_GObj = a_StaticPlayer_0 + 0xB0

(a_Fighter_GObj,) = struct.unpack(">I", mem.read(0x80453130, 4))

Fighter_GObj = mem.read(a_Fighter_GObj, 0x38) # sizeof(Fighter_GObj)
p_Fighter, = struct.unpack('>I', Fighter_GObj[0x2C:0x2C+4])

# Fighter = mem.read(p_Fighter, 0x23EC) # sizeof(Fighter)

def val(ptr, fmt, size=4):
    buf = mem.read(ptr, size)
    return struct.unpack('>' + fmt, buf)

IPython.embed()
