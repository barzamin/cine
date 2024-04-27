import struct
import logging
from dataclasses import dataclass

import IPython
import numpy as np

from memory import DOLMemory
from util import hexdump
from melee import FighterKind, FighterBone, JObj_Flags, JObj
from melee import P_PLAYER_SLOTS, PLAYER_SLOT_SIZE

logging.basicConfig(level=logging.INFO)
np.set_printoptions(linewidth=120)

mem = DOLMemory()

slot = 0
p_StaticPlayer = P_PLAYER_SLOTS + PLAYER_SLOT_SIZE * slot

p_p_Fighter_GObj = p_StaticPlayer + 0xB0
p_Fighter_GObj = mem.readv(p_p_Fighter_GObj, "I")
p_Fighter = mem.readv(p_Fighter_GObj + 0x2C, "I")


## figure out how many parts there are in the bone table
fighter_kind = mem.readv(p_Fighter + 0x4, "I")
ftPartsTable = mem.readv(0x804D6544, "I")
fighter_ftParts = mem.readv(ftPartsTable + fighter_kind * 4, "I")
parts_num = mem.readv(fighter_ftParts + 0x8, "I")

## bone table
# FighterBone[]
# sizeof(FighterBone) == 0x10
p_bone_table = mem.readv(p_Fighter + 0x5E8, "I")

fighter_bones = [
    FighterBone.from_bytes(mem.read(p_bone_table + idx * 0x10, 0x10))
    for idx in range(parts_num)
]

# jobjs = {}
# for bone in fighter_bones:
#     jobjs[bone.p_joint] = JObj.from_mem(mem, bone.p_joint)

# p_root_jobj = fighter_bones[0].p_joint
# assert JObj_Flags.SKELETON_ROOT in jobjs[p_root_jobj].flags

class RenderableJObj(JObj):
    @classmethod
    def from_mem(cls, mem, p_jobj, parent=None):
        self = super().from_mem(mem, p_jobj)

        self.parent = parent
        self.child = self.sister = None
        if self.p_child:
            self.child = cls.from_mem(mem, self.p_child, parent=self)
        if self.p_next:
            self.child = cls.from_mem(mem, self.p_next, parent=self)

        return self

    def recompute_transforms(self):
        txf_local = mat_scale(self.scale) @ mat_quat(self.rotate) @ mat_translate(self.translate)

        if self.parent:
            # txf_world =

root_jobj = RenderableJObj.from_mem(mem, fighter_bones[0].p_joint)
assert JObj_Flags.SKELETON_ROOT in root_jobj.flags

