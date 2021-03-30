import ctypes
from ctypes import wintypes
import time, os

c_ulong = ctypes.c_ulong
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", c_ulong),
        ("dwTime", c_ulong) ]

lastInputInfo = LASTINPUTINFO()
lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
while True:    
    errorCode = ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    lastInputTime = lastInputInfo.dwTime
    kernel32 = ctypes.windll.kernel32
    tickCount = kernel32.GetTickCount()
    time.sleep(.06)
