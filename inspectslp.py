import sys
import struct
from io import BytesIO
from os import SEEK_CUR
from enum import Enum, IntEnum
from pprint import pprint
from itertools import islice
from logging import getLogger
import warnings

import click
import IPython

from util import hexdump
from melee import FighterKind

logger = getLogger(__name__)


class CommandId(IntEnum):
    SPLIT_MESSAGE = 0x10
    DESCRIPTIONS = 0x35
    GAME_INFO = 0x36
    GECKO_LIST = 0x3D
    INITIAL_RNG = 0x3A
    PRE_FRAME = 0x37
    POST_FRAME = 0x38
    ITEM = 0x3B
    FRAME_BOOKEND = 0x3C
    GAME_END = 0x39
    BONES = 0x60


def parse_packet(f, cmd_id, length_hint=None):
    match cmd_id:
        case CommandId.DESCRIPTIONS:
            payload_size = struct.unpack('>B', f.read(1))[0]
            cursor = 0
            command_sizes = []
            while cursor < payload_size - 1:
                cmd_byte = CommandId(struct.unpack('>B', f.read(1))[0])
                cmd_size = struct.unpack('>H', f.read(2))[0]

                command_sizes.append((cmd_byte, cmd_size))
                cursor += 3

            return {'command_sizes': command_sizes}

        case CommandId.GAME_INFO:
            # skip for now
            f.seek(0x2f9-1, SEEK_CUR)
            return None

        case CommandId.SPLIT_MESSAGE:
            message_block = f.read(0x200)
            actual_size = struct.unpack('>H', f.read(2))[0]
            chunk_internal_cmd = CommandId(struct.unpack('>B', f.read(1))[0])
            is_last = struct.unpack('>?', f.read(1))[0]

            return {'message_block': message_block,
                    'actual_size': actual_size,
                    'chunk_internal_cmd': chunk_internal_cmd,
                    'is_last': is_last}

        case CommandId.GECKO_LIST:
            # skip for now
            return None

        case CommandId.BONES:
            # print(f'wooooooo bones ({length_hint = })')
            return {
                'frame_idx': struct.unpack('>i', f.read(4))[0],
                'player_idx': struct.unpack('>B', f.read(1))[0],
                'chara_id': FighterKind(struct.unpack('>Bx', f.read(2))[0]),
                # 'bonedat_size': struct.unpack('>I', f.read(4))[0],
            }

        case CommandId.INITIAL_RNG:
            return {
                'frame': struct.unpack('>i', f.read(4))[0],
                'seed': struct.unpack('>I', f.read(4))[0],
                'scene_frame_counter': struct.unpack('>I', f.read(4))[0],
            }

        case CommandId.PRE_FRAME:
            _ = f.read(0x40)
            return None

        case CommandId.POST_FRAME:
            _ = f.read(0x54)
            return None

        case CommandId.FRAME_BOOKEND:
            return {
                'frame': struct.unpack('>i', f.read(4))[0],
                'latest_finalized_frame': struct.unpack('>i', f.read(4))[0],
            }

        case CommandId.ITEM:
            _ = f.read(44)
            return None

        case _:
            raise NotImplementedError(f'parse_packet: unimplemented packet type {cmd_id!r}')

def _inner_read_packets(f):
    while True:
        buf = f.read(1)
        cmd_id = CommandId(struct.unpack('>B', buf)[0])

        yield {'id': cmd_id, 'packet': parse_packet(f, cmd_id)}

def read_packets(f):
    cur_split_cmd = None
    rollup_buf = None
    rollup_len = 0
    for packet in _inner_read_packets(f):
        logger.debug(f"-- processing {packet['id'] = !r}")
        if packet['id'] == CommandId.SPLIT_MESSAGE:
            if not cur_split_cmd:
                logger.debug(f"beginning split message reprocessing (wrapping {packet['packet']['chunk_internal_cmd']!r})")
                rollup_buf = bytearray()
                cur_split_cmd = packet['packet']['chunk_internal_cmd']

            assert cur_split_cmd == packet['packet']['chunk_internal_cmd'], 'you cant start wrapping a different command before you is_last=True, silly'

            rollup_buf += packet['packet']['message_block']
            rollup_len += packet['packet']['actual_size']

            if packet['packet']['is_last']:
                # reprocess/yield the aggregate packet's contents and reset the splitter state machine
                logger.debug(f'split is over; yielding a packet of type {cur_split_cmd!r}')
                yield {'id': cur_split_cmd,
                       'packet': parse_packet(BytesIO(rollup_buf),
                                              cur_split_cmd,
                                              length_hint=rollup_len)}, rollup_buf

                cur_split_cmd = None
                rollup_buf = None
                rollup_len = 0

        else:
            yield packet, None

@click.command()
@click.argument('slppath', type=click.Path())
@click.option('--head', type=int, default=None)
def cli(slppath, head):
    with open(slppath, 'rb') as f:
        f.seek(11)

        buf = f.read(4)
        raw_len = struct.unpack('>I', buf)[0]
        # assert raw_len == 0, "for now, only working with truncated replays since kellz' patch acts busted"

        # for p in _inner_read_packets(f):
        #     if p['id'] == CommandId.DESCRIPTIONS:
        #         print(p)
        #     print(repr(p['id']))

        pkgen = read_packets(f)
        if head: pkgen = islice(pkgen, head)
        for packet, buf in pkgen:
            if packet['id'] == CommandId.BONES and packet['packet']['frame_idx'] == -94:
                pprint(packet)
                print('\n--------------------------------\n')
                # print(hexdump(buf))
                with open('bones.bin', 'wb') as f: f.write(buf)
                break

if __name__ == '__main__':
    cli()
