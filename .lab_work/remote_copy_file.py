import struct
source = 'C:\\Users\\Xxthe\\Downloads\\Hamdan.txt'
assert Path(source).exists()
h = next(w['handle'] for w in rdp_windows() if w['class'] == 'TscShellContainerClass')
focus(h)
payload = struct.pack('<IiiII',20,0,0,0,1) + (source+'\0\0').encode('utf-16-le')
win32clipboard.OpenClipboard()
try:
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_HDROP,payload)
finally:
    win32clipboard.CloseClipboard()
time.sleep(2)
keys('^v')
time.sleep(4)
screenshot(h,'C:/Users/Xxthe/Parallel_lab/.lab_work/rdp.png')
