from pathlib import Path
import subprocess
import ctypes
import json
import time
import sys
import os
import win32gui
import win32ui
from PIL import Image

ROOT = Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3')
WORK = ROOT / 'work'
EVIDENCE = WORK / 'evidence'
DOWNLOADS = Path('C:/Users/Xxthe/Downloads')
for folder in [WORK, EVIDENCE, ROOT / 'output']:
    folder.mkdir(parents=True, exist_ok=True)
ps = WORK / 'local_date.ps1'
ps.write_text('''$Host.UI.RawUI.WindowTitle = 'CCEN 448 Lab 3 - Local date command'
$Host.UI.RawUI.BackgroundColor = 'Black'
$Host.UI.RawUI.ForegroundColor = 'White'
Clear-Host
Set-Location -LiteralPath 'C:\\Users\\Xxthe\\Downloads'
Write-Host 'PS C:\\Users\\Xxthe\\Downloads> Get-Date -Format o | Out-File -FilePath "Hamdan.txt"'
Get-Date -Format o | Out-File -FilePath "Hamdan.txt"
Write-Host ''
Write-Host 'PS C:\\Users\\Xxthe\\Downloads> Get-Content Hamdan.txt'
Get-Content -LiteralPath 'Hamdan.txt'
Write-Host ''
Write-Host 'PS C:\\Users\\Xxthe\\Downloads>'
Set-Content -LiteralPath 'C:\\Users\\Xxthe\\OneDrive\\Desktop\\Cloud_Lab\\Lab3\\work\\date_ready.txt' -Value 'ready'
Read-Host 'Press Enter to close'
''', encoding='utf-8')
if (DOWNLOADS / 'Hamdan.txt').exists():
    raise RuntimeError('Hamdan.txt already exists in Downloads; inspect before replacing.')
startup = subprocess.STARTUPINFO()
startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
subprocess.Popen(['conhost.exe', 'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ps)], startupinfo=startup)
deadline = time.monotonic() + 30
while not (WORK / 'date_ready.txt').exists():
    if time.monotonic() > deadline:
        raise TimeoutError('Local date command')
    time.sleep(.5)
windows = []
win32gui.EnumWindows(lambda h, _: windows.append(h) if win32gui.GetWindowText(h) == 'CCEN 448 Lab 3 - Local date command' else None, None)
if not windows:
    raise RuntimeError('Local console window not found')
hwnd = windows[0]
left, top, right, bottom = win32gui.GetWindowRect(hwnd)
width, height = right-left, bottom-top
dc_handle = win32gui.GetWindowDC(hwnd)
src = win32ui.CreateDCFromHandle(dc_handle)
mem = src.CreateCompatibleDC()
bitmap = win32ui.CreateBitmap()
bitmap.CreateCompatibleBitmap(src, width, height)
mem.SelectObject(bitmap)
if not ctypes.windll.user32.PrintWindow(hwnd, mem.GetSafeHdc(), 2):
    raise RuntimeError('Console capture failed')
image = Image.frombuffer('RGB', (width,height), bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
image.save(EVIDENCE / '10_local_date.png')
win32gui.DeleteObject(bitmap.GetHandle())
mem.DeleteDC()
src.DeleteDC()
win32gui.ReleaseDC(hwnd, dc_handle)
win32gui.PostMessage(hwnd, 0x0010, 0, 0)
data = (DOWNLOADS / 'Hamdan.txt').read_bytes()
(WORK / 'Hamdan.txt').write_bytes(data)
print(json.dumps({'date_file': str(DOWNLOADS / 'Hamdan.txt'), 'contents': data.decode('utf-16').strip(), 'screenshot': str(EVIDENCE / '10_local_date.png')}))
