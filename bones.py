import struct
import logging
from dataclasses import dataclass

import IPython
import numpy as np

from memory import DOLMemory
from util import hexdump
from melee import FighterKind, FighterBone, JObj_Flags

# logging.basicConfig(level=logging.DEBUG)
np.set_printoptions(linewidth=120)

mem = DOLMemory()

def val(ptr, fmt, size=4):
    buf = mem.read(ptr, size)
    vals = struct.unpack('>' + fmt, buf)
    if len(vals) == 1:
        return vals[0]
    else:
        return list(vals)

def npval(ptr, shape) -> np.array:
    nw = int(np.prod(shape))
    vals = struct.unpack(f'>{nw}f', mem.read(ptr, 4 * nw))
    return np.array(vals).reshape(shape)

player_slots = 0x80453080
slot = 0
p_StaticPlayer = player_slots + 0xe90 * slot

p_p_Fighter_GObj = p_StaticPlayer + 0xB0
p_Fighter_GObj = val(p_p_Fighter_GObj, 'I')
p_Fighter = val(p_Fighter_GObj + 0x2c, 'I')


## figure out how many parts there are in the bone table
fighter_kind = val(p_Fighter + 0x4, 'I')
# FighterPartsTable** ftPartsTable
# comes from PlCo.dat
# indexed by fighter_kind
ftPartsTable = val(0x804D6544, 'I')
# typedef struct _FighterPartsTable {
#     u8* joint_to_part;
#     u8* part_to_joint;
#     u32 parts_num;
# } FighterPartsTable;
fighter_ftParts = val(ftPartsTable + fighter_kind * 4, 'I')
parts_num = val(fighter_ftParts + 0x8, 'I')

## bone table
# FighterBone[]
# sizeof(FighterBone) == 0x10
p_bone_table = val(p_Fighter + 0x5e8, 'I')

parts = [FighterBone.from_bytes(mem.read(p_bone_table + idx*0x10, 0x10)) for idx in range(parts_num)]

@dataclass
class JObj:
    flags: int
    rotate: np.array
    scale: np.array
    translate: np.array
    mtx: np.array

    @classmethod
    def from_mem(cls, p_jobj):
        flags = JObj_Flags(val(p_jobj + 0x14, 'I'))
        rotate = npval(p_jobj + 0x1c, (4,)) # Quaternion
        scale = npval(p_jobj + 0x38, (3,)) # Vec3
        translate = npval(p_jobj + 0x1c, (3,)) # Vec3
        mtx = npval(p_jobj + 0x44, (3,4)) # Mtx

        return cls(flags=flags,
                   rotate=rotate,
                   scale=scale,
                   translate=translate,
                   mtx=mtx)

# def dump_jobj(p_jobj, depth=0):
#     idt = '  ' * depth
#     print(idt + f'{p_jobj:x}')
#     print(idt + f' \\- flags:{flags}')
#     print(idt + f' |- {rotate=}')
#     print(idt + f' |- {scale=}')
#     print(idt + f' |- {translate=}')

def walk_jobj(p_jobj, depth=0):
    dump_jobj(p_jobj, depth=depth)

    p_child = val(p_jobj + 0x10, 'I')
    if p_child != 0:
        dump_jobj(p_child, depth=depth+1)

    p_next = val(p_jobj + 0x08, 'I')
    if p_next != 0:
        dump_jobj(p_next, depth=depth)

# dump_jobj(parts[0].p_joint)

IPython.embed()
