from logging import getLogger
import struct
import ctypes
from ctypes import windll, WinError
from ctypes import Structure, Union, sizeof, pointer
from ctypes import c_char, c_ulong, c_long, c_size_t, c_void_p
from ctypes.wintypes import DWORD, WORD, LPCVOID

import numpy as np

from win32ty import *

logger = getLogger(__name__)

kernel32 = windll.kernel32
psapi = windll.psapi

# DOL/RVL stuff
GC_RAM_START = 0x80000000
GC_RAM_END = 0x81800000
GC_RAM_SIZE = 0x2000000


def _get_dolphin_proc_handle():
    hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)

    res = kernel32.Process32First(hProcessSnap, pe32)

    VALID_NAMES = {"Slippi_Dolphin.exe", "Slippi Dolphin.exe"}

    proc_handle = None
    ret_code = DWORD(0)
    while res:
        proc_name = pe32.szExeFile.decode()
        if proc_name in VALID_NAMES:
            hProcess = kernel32.OpenProcess(
                PROCESS_VM_OPERATION + PROCESS_VM_READ + PROCESS_QUERY_INFORMATION,
                False,
                pe32.th32ProcessID,
            )

            if hProcess:
                if (
                    kernel32.GetExitCodeProcess(hProcess, pointer(ret_code))
                    and ret_code.value == STILL_ACTIVE
                ):
                    proc_handle = hProcess
                    break
                else:
                    kernel32.CloseHandle(hProcess)
                    break

        res = kernel32.Process32Next(hProcessSnap, pointer(pe32))

    kernel32.CloseHandle(hProcessSnap)

    return proc_handle


def _find_dol_ram_region(hProc):
    mem_info = MEMORY_BASIC_INFORMATION()
    p = 0

    while kernel32.VirtualQueryEx(
        hProc, LPCVOID(p), pointer(mem_info), sizeof(mem_info)
    ) == sizeof(mem_info):
        p += mem_info.RegionSize
        # print(f'{p = :x}')
        # print(f'{mem_info.RegionSize = :x}')

        if (
            mem_info.RegionSize >= GC_RAM_SIZE
            and mem_info.RegionSize % GC_RAM_SIZE == 0
            and mem_info.Type == MEM_MAPPED
        ):
            ws_info = PSAPI_WORKING_SET_EX_INFORMATION()
            ws_info.VirtualAddress = mem_info.BaseAddress

            if psapi.QueryWorkingSetEx(hProc, pointer(ws_info), sizeof(ws_info)):
                flags = ws_info.VirtualAttributes.Flags
                base = mem_info.BaseAddress
                size = mem_info.RegionSize

                # check Valid bit. MSVC says first field <=> least significant bit.
                valid = (flags & (1 << 0)) != 0

                if valid and base != 0:
                    # go with the first region
                    # print(f'{flags=:b} {base=:x} {size=:x}')
                    return (base, size)


class DOLMemory:
    def __init__(self):
        self.hProc = _get_dolphin_proc_handle()
        self.dol_ram_base, self.dol_ram_size = _find_dol_ram_region(self.hProc)

    def read(self, addr, size):
        buf = ctypes.create_string_buffer(size)

        if addr >= GC_RAM_START and addr <= GC_RAM_END:
            offset = addr % GC_RAM_START
        else:
            raise ValueError(f"invalid read location: {addr:x}")

        vaddr = self.dol_ram_base + offset
        read_bytes = c_size_t(0)

        ret = kernel32.ReadProcessMemory(
            self.hProc, vaddr, buf, size, pointer(read_bytes)
        )
        if not ret:
            raise WinError()

        if read_bytes.value != size:
            raise RuntimeError(f"asked for {size} bytes, only read {read_bytes}")
            # raise RuntimeError(f'read from {addr:x} (process addr {vaddr:x}) failed')

        logger.debug(f"read {read_bytes.value}bytes from {addr:08x}")

        return ctypes.string_at(buf, size=size)

    def readv(self, ptr: int, fmt: str, size: int = None):
        """
        read a value with given struct 'fmt'. implicitly big endian.

        if fmt only contains one value, it's unwrapped from the tuple.
        otherwise, we convert it to a list before returning
        (in case u wanna use np.array() or sth <3)

        note that `size` is only provided as a convenience if
        struct.calcsize is busted for some reason ??
        """
        st = struct.Struct(
            ">" + fmt
        )  # cached internally by struct (see the Note in struct.Struct)
        size = size or st.size

        buf = self.read(ptr, size)
        vals = st.unpack(buf)

        # implicit nonsense :3
        if len(vals) == 1:
            return vals[0]
        else:
            return list(vals)

    def readnp32(self, ptr: int, shape: tuple[int]):
        """
        read a packed fp32 array of a given shape into an np.ndarray.
        assumes contiguity/no intra-array padding
        """

        nw = int(np.prod(shape))
        vals = struct.unpack(f">{nw}f", self.read(ptr, 4 * nw))
        return np.array(vals).reshape(shape)
