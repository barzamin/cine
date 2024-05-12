import re
from pprint import pprint
from typing import Any

import IPython
import click
import numpy as np

from memory import DOLMemory
from petrautil.hexdump import hexdump
from melee import FighterKind, FighterBone, JObj_Flags, JObj
from melee import P_PLAYER_SLOTS, PLAYER_SLOT_SIZE


def get_logged_poses(f) -> dict[str, Any]:
    poses = {}
    frame_id = None
    rx = re.compile(
        r"\[Frame: (-?\d+)\] \[Bone Transforms\] Idx: (\d+) \(0x([0-9a-f]+)\), Pos: \(([-.\d ,]+)\), Rot: \(([-.\d ,]+)\)"
    )
    for line in f:
        if m := rx.search(line):
            this_frame, idx, addr, pos, rot = m.groups()
            this_frame = int(this_frame)
            idx = int(idx)
            addr = int(addr, 16)
            pos = np.array([float(x.strip()) for x in pos.split(",")])
            rot = np.array([float(x.strip()) for x in rot.split(",")])

            if not frame_id:
                frame_id = this_frame
            assert frame_id == this_frame  # only one frame in trace

            assert idx not in poses
            poses[idx] = {
                "addr": addr,
                "pos": pos,
                "rot": rot,
            }

    return poses


@click.command()
@click.argument("logtext", type=click.Path())
def cli(logtext):
    np.set_printoptions(linewidth=120)

    with open(logtext) as f:
        logged_poses = get_logged_poses(f)

    ## now do our side
    mem = DOLMemory()

    slot = 0
    p_StaticPlayer = P_PLAYER_SLOTS + PLAYER_SLOT_SIZE * slot

    p_p_Fighter_GObj = p_StaticPlayer + 0xB0
    p_Fighter_GObj = mem.readv(p_p_Fighter_GObj, "I")
    p_Fighter = mem.readv(p_Fighter_GObj + 0x2C, "I")

    # get bone table size
    fighter_kind = mem.readv(p_Fighter + 0x4, "I")
    ftPartsTable = mem.readv(0x804D6544, "I")
    fighter_ftParts = mem.readv(ftPartsTable + fighter_kind * 4, "I")
    parts_num = mem.readv(fighter_ftParts + 0x8, "I")

    # pointer to bone table
    p_bone_table = mem.readv(p_Fighter + 0x5E8, "I")

    bones = [
        FighterBone.from_bytes(mem.read(p_bone_table + idx * 0x10, 0x10))
        for idx in range(parts_num)
    ]

    read_poses = [JObj.from_mem(mem, bone.p_joint) for bone in bones]

    print("joint        .")
    for idx, log_pose in logged_poses.items():
        read_pose = read_poses[idx]

        def fmta(a):
            return " ".join(f"{x:9.2E}" for x in a)

        print(
            "{:02}    logged | pos: {:32} rot: {:32}".format(
                idx,
                fmta(log_pose["pos"]),
                fmta(log_pose["rot"]),
            )
        )
        print(
            "{:02}      read | pos: {:32} rot: {:32}".format(
                idx,
                fmta(read_pose.translate),
                fmta(read_pose.rotate),
            )
        )

        ATOL = 1e-6
        pos_ok = np.allclose(log_pose["pos"], read_pose.translate, atol=ATOL)
        rot_ok = np.allclose(log_pose["rot"], read_pose.rotate, atol=ATOL)
        pos_delta = log_pose["pos"] - read_pose.translate
        rot_delta = log_pose["rot"] - read_pose.rotate
        print(
            "{:02}         Δ | pos: {:29} {} rot: {:30} {}".format(
                idx,
                fmta(pos_delta),
                "✅" if pos_ok else "❌",
                fmta(rot_delta),
                "✅" if rot_ok else "❌",
            )
        )


if __name__ == "__main__":
    cli()
