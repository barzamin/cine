from ctypes import Structure, Union, sizeof, pointer
from ctypes import c_char, c_ulong, c_long, c_size_t, c_void_p
from ctypes.wintypes import DWORD, WORD, LPCVOID

TH32CS_SNAPPROCESS = 0x2
PROCESS_VM_OPERATION = 0x8
PROCESS_VM_READ = 0x10
PROCESS_VM_WRITE = 0x20
PROCESS_QUERY_INFORMATION = 0x400
STILL_ACTIVE = 259
MAX_PATH = 260
MEM_MAPPED = 0x40000

ULONG_PTR = c_size_t
PVOID = c_void_p


class PROCESSENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ProcessID", DWORD),
        ("th32DefaultHeapID", ULONG_PTR),
        ("th32ModuleID", DWORD),
        ("cntThreads", DWORD),
        ("th32ParentProcessID", DWORD),
        ("pcPriClassBase", c_long),
        ("dwFlags", DWORD),
        ("szExeFile", c_char * MAX_PATH),
    ]


class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", PVOID),
        ("AllocationBase", PVOID),
        ("AllocationProtect", DWORD),
        ("PartitionId", WORD),
        ("RegionSize", c_size_t),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD),
    ]


class PSAPI_WORKING_SET_EX_BLOCK(Union):
    _fields_ = [
        ("Flags", ULONG_PTR),
        # some union shit
    ]


class PSAPI_WORKING_SET_EX_INFORMATION(Structure):
    _fields_ = [
        ("VirtualAddress", PVOID),
        ("VirtualAttributes", PSAPI_WORKING_SET_EX_BLOCK),
    ]
