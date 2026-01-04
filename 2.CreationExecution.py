from ctypes import *
import sys
from ctypes import wintypes
import subprocess

try:
    from ctypes import windll
except ImportError:
    print("windll is only available on Windows.")
    sys.exit(1)
kernal32 = windll.kernel32
SIZE_T = c_size_t
LPSTR = POINTER(c_char)
LPBYTE = POINTER(c_ubyte)


virtual_alloc_ex = kernal32.VirtualAllocEx
virtual_alloc_ex.argtypes = (wintypes.HANDLE, wintypes.LPVOID, SIZE_T, wintypes.DWORD, wintypes.DWORD)
virtual_alloc_ex.restype = wintypes.LPVOID

write_process_memory = kernal32.WriteProcessMemory
write_process_memory.argtypes = (wintypes.HANDLE, wintypes.LPVOID,wintypes.LPCVOID, SIZE_T, POINTER(SIZE_T))
write_process_memory.restype = wintypes.BOOL
                        
class _SECUITY_ATTRIBUTES(Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    ]
LPSECURITY_ATTRIBUTES = POINTER(_SECUITY_ATTRIBUTES)
LPSECURITY_ATTRIBUTES = POINTER(_SECUITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = wintypes.LPVOID
CreateRemoteThread = kernal32.CreateRemoteThread
CreateRemoteThread.argtypes = (
    wintypes.HANDLE,
    LPSECURITY_ATTRIBUTES,
    SIZE_T,
    LPTHREAD_START_ROUTINE,
    wintypes.LPVOID,
    wintypes.DWORD,
    POINTER(wintypes.DWORD),
)
CreateRemoteThread.restype = wintypes.HANDLE

MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
EXECUTE_IMMEDIATELY = 0x0
PROCESS_ALL_ACCESS = 0x1F0FFF

virtual_free_ex = kernal32.VirtualFreeEx
virtual_free_ex.argtypes = (wintypes.HANDLE, wintypes.LPVOID,
                                SIZE_T, wintypes.DWORD)
virtual_free_ex.restype = wintypes.BOOL

process = subprocess.Popen(["notepad.exe"])
pid = process.pid
h_process = kernal32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
dll_path = b"C:\\Path\\To\\Your\\DLL.dll"
arg_address = virtual_alloc_ex(h_process, None, len(dll_path), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
written = SIZE_T(0)
if not write_process_memory(h_process, arg_address, dll_path, len(dll_path), byref(written)):
    raise OSError("WriteProcessMemory failed")
print(f"[+] Written {written.value} bytes to remote process")
load_library_a_addr = kernal32.GetProcAddress(kernal32._handle, b"LoadLibraryA")
if not load_library_a_addr:
    raise OSError("GetProcAddress failed")
thread_id = wintypes.DWORD(0)
h_thread = CreateRemoteThread(h_process, None, 0,
                              load_library_a_addr,
                              arg_address,
                              0,
                              byref(thread_id))
if not h_thread:
    raise OSError("CreateRemoteThread failed")
print(f"[+] Remote thread handle: {h_thread:#x}")
print(f"[+] Remote thread ID: {thread_id.value}")
print("[+] DLL injection successful")