import struct
import logging
from dataclasses import dataclass

import IPython
import numpy as np

from memory import DOLMemory
from util import hexdump
from melee import FighterKind, FighterBone, JObj_Flags, JObj
from melee import P_PLAYER_SLOTS, PLAYER_SLOT_SIZE

# logging.basicConfig(level=logging.DEBUG)
np.set_printoptions(linewidth=120)

mem = DOLMemory()

slot = 0
p_StaticPlayer = P_PLAYER_SLOTS + PLAYER_SLOT_SIZE * slot

p_p_Fighter_GObj = p_StaticPlayer + 0xB0
p_Fighter_GObj = mem.readv(p_p_Fighter_GObj, "I")
p_Fighter = mem.readv(p_Fighter_GObj + 0x2C, "I")


## figure out how many parts there are in the bone table
fighter_kind = mem.readv(p_Fighter + 0x4, "I")
# FighterPartsTable** ftPartsTable
# comes from PlCo.dat
# indexed by fighter_kind
ftPartsTable = mem.readv(0x804D6544, "I")
# typedef struct _FighterPartsTable {
#     u8* joint_to_part;
#     u8* part_to_joint;
#     u32 parts_num;
# } FighterPartsTable;
fighter_ftParts = mem.readv(ftPartsTable + fighter_kind * 4, "I")
parts_num = mem.readv(fighter_ftParts + 0x8, "I")

## bone table
# FighterBone[]
# sizeof(FighterBone) == 0x10
p_bone_table = mem.readv(p_Fighter + 0x5E8, "I")

parts = [
    FighterBone.from_bytes(mem.read(p_bone_table + idx * 0x10, 0x10))
    for idx in range(parts_num)
]

# def dump_jobj(p_jobj, depth=0):
#     idt = '  ' * depth
#     print(idt + f'{p_jobj:x}')
#     print(idt + f' \\- flags:{flags}')
#     print(idt + f' |- {rotate=}')
#     print(idt + f' |- {scale=}')
#     print(idt + f' |- {translate=}')


# def walk_jobj(p_jobj, depth=0):
#     dump_jobj(p_jobj, depth=depth)

#     p_child = mem.readv(p_jobj + 0x10, "I")
#     if p_child != 0:
#         dump_jobj(p_child, depth=depth + 1)

#     p_next = mem.readv(p_jobj + 0x08, "I")
#     if p_next != 0:
#         dump_jobj(p_next, depth=depth)


# dump_jobj(parts[0].p_joint)
for i, bone in enumerate(parts):
    print(f" --- {i:02} --- ")
    jobj = JObj.from_mem(mem, bone.p_joint)
    print(f"""{bone.p_joint:08x}
    {jobj.translate=}
    {jobj.rotate=}
    {jobj.flags=}""")


# IPython.embed()
