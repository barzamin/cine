import struct
import logging
from pprint import pprint
from dataclasses import dataclass

import IPython
import numpy as np

from memory import DOLMemory
from melee import FighterKind, FighterBone, JObj_Flags, JObj, Melee
from petrautil.hexdump import hexdump

# logging.basicConfig(level=logging.DEBUG)
np.set_printoptions(linewidth=120)

mem = DOLMemory()
melee = Melee(mem)

fighter = melee.get_fighter(slot=0)
parts = fighter.get_fighterbones()

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
    # print(f"""{bone.p_joint:08x}
    # {jobj.translate=}
    # {jobj.rotate=}
    # {jobj.flags=}""")
    pprint(jobj)


# IPython.embed()
