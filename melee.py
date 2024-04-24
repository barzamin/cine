import struct
from enum import IntEnum, Flag, IntFlag, auto
from dataclasses import dataclass

import numpy as np

from memory import DOLMemory

### addresses/constants ###
P_PLAYER_SLOTS = 0x80453080
PLAYER_SLOT_SIZE = 0xE90


####
class JObj_Flags(Flag):
    SKELETON = 1 << 0
    SKELETON_ROOT = 1 << 1
    ENVELOPE_MODEL = 1 << 2
    CLASSICAL_SCALE = 1 << 3
    HIDDEN = 1 << 4
    PTCL = 1 << 5
    MTX_DIRTY = 1 << 6
    LIGHTING = 1 << 7
    TEXGEN = 1 << 8
    INSTANCE = 1 << 12
    SPLINE = 1 << 14
    FLIP_IK = 1 << 15
    SPECULAR = 1 << 16
    USE_QUATERNION = 1 << 17
    UNK_B18 = 1 << 18
    UNK_B19 = 1 << 19
    UNK_B20 = 1 << 20
    NULL_OBJ = 0 << 21
    JOINT1 = 1 << 21
    JOINT2 = 2 << 21
    JOINT = 3 << 21
    EFFECTOR = 3 << 21
    USER_DEF_MTX = 1 << 23
    MTX_INDEP_PARENT = 1 << 24
    MTX_INDEP_SRT = 1 << 25
    UNK_B26 = 1 << 26
    UNK_B27 = 1 << 27
    ROOT_OPA = 1 << 28
    ROOT_XLU = 1 << 29
    ROOT_TEXEDGE = 1 << 30


@dataclass
class JObj:
    flags: JObj_Flags
    rotate: np.array
    scale: np.array
    translate: np.array
    mtx: np.array

    # linked pointers
    p_next: int
    p_parent: int
    p_child: int

    @classmethod
    def from_mem(cls, mem: DOLMemory, p_jobj):
        flags = mem.readv(p_jobj + 0x14, "I")
        print(f'flags: {flags:08x}')
        flags = JObj_Flags(flags)
        rotate = mem.readnp32(p_jobj + 0x1C, (4,))  # Quaternion
        scale = mem.readnp32(p_jobj + 0x2C, (3,))  # Vec3
        translate = mem.readnp32(p_jobj + 0x38, (3,))  # Vec3
        mtx = mem.readnp32(p_jobj + 0x44, (3, 4))  # Mtx

        p_next   = mem.readv(p_jobj + 0x08, "I")
        p_parent = mem.readv(p_jobj + 0x0c, "I")
        p_child  = mem.readv(p_jobj + 0x10, "I")

        return cls(
            flags=flags,
            rotate=rotate,
            scale=scale,
            translate=translate,
            mtx=mtx,

            p_next=p_next,
            p_parent=p_parent,
            p_child=p_child
        )


@dataclass
class FighterBone:
    p_joint: int
    p_jobj2: int
    flags: int

    @classmethod
    def from_bytes(cls, buf):
        # ignore padding junk
        p_joint, p_jobj2, flags = struct.unpack(">IIBxxxxxxx", buf)

        return cls(p_joint, p_jobj2, flags)


###


class FighterKind(IntEnum):
    FTKIND_MARIO = 0
    FTKIND_FOX = auto()
    FTKIND_CAPTAIN = auto()
    FTKIND_DONKEY = auto()
    FTKIND_KIRBY = auto()
    FTKIND_KOOPA = auto()
    FTKIND_LINK = auto()
    FTKIND_SEAK = auto()
    FTKIND_NESS = auto()
    FTKIND_PEACH = auto()
    FTKIND_POPO = auto()
    FTKIND_NANA = auto()
    FTKIND_PIKACHU = auto()
    FTKIND_SAMUS = auto()
    FTKIND_YOSHI = auto()
    FTKIND_PURIN = auto()
    FTKIND_MEWTWO = auto()
    FTKIND_LUIGI = auto()
    FTKIND_MARS = auto()
    FTKIND_ZELDA = auto()
    FTKIND_CLINK = auto()
    FTKIND_DRMARIO = auto()
    FTKIND_FALCO = auto()
    FTKIND_PICHU = auto()
    FTKIND_GAMEWATCH = auto()
    FTKIND_GANON = auto()
    FTKIND_EMBLEM = auto()
    FTKIND_MASTERH = auto()
    FTKIND_CREZYH = auto()
    FTKIND_BOY = auto()
    FTKIND_GIRL = auto()
    FTKIND_GKOOPS = auto()
    FTKIND_SANDBAG = auto()
    FTKIND_MAX = FTKIND_NONE = auto()


class Fighter_Part(IntEnum):
    FtPart_TopN = 0
    FtPart_TransN = auto()
    FtPart_XRotN = auto()
    FtPart_YRotN = auto()
    FtPart_HipN = auto()
    FtPart_WaistN = auto()
    FtPart_LLegJA = auto()
    FtPart_LLegJ = auto()
    FtPart_LKneeJ = auto()
    FtPart_LFootJA = auto()
    FtPart_LFootJ = auto()
    FtPart_RLegJA = auto()
    FtPart_RLegJ = auto()
    FtPart_RKneeJ = auto()
    FtPart_RFootJA = auto()
    FtPart_RFootJ = auto()
    FtPart_BustN = auto()
    FtPart_LShoulderN = auto()
    FtPart_LShoulderJA = auto()
    FtPart_LShoulderJ = auto()
    FtPart_LArmJ = auto()
    FtPart_LHandN = auto()
    FtPart_L1stNa = auto()
    FtPart_L1stNb = auto()
    FtPart_L2ndNa = auto()
    FtPart_L2ndNb = auto()
    FtPart_L3rdNa = auto()
    FtPart_L3rdNb = auto()
    FtPart_L4thNa = auto()
    FtPart_L4thNb = auto()
    FtPart_LThumbNa = auto()
    FtPart_LThumbNb = auto()
    FtPart_LHandNb = auto()
    FtPart_NeckN = auto()
    FtPart_HeadN = auto()
    FtPart_RShoulderN = auto()
    FtPart_RShoulderJA = auto()
    FtPart_RShoulderJ = auto()
    FtPart_RArmJ = auto()
    FtPart_RHandN = auto()
    FtPart_R1stNa = auto()
    FtPart_R1stNb = auto()
    FtPart_R2ndNa = auto()
    FtPart_R2ndNb = auto()
    FtPart_R3rdNa = auto()
    FtPart_R3rdNb = auto()
    FtPart_R4thNa = auto()
    FtPart_R4thNb = auto()
    FtPart_RThumbNa = auto()
    FtPart_RThumbNb = auto()
    FtPart_RHandNb = auto()
    FtPart_ThrowN = auto()
    FtPart_TransN2 = auto()
    FtPart_109 = 109
