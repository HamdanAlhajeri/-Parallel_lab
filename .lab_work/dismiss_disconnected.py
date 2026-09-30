for w in rdp_windows():
    if w['class']=='#32770':
        buttons=[]
        win32gui.EnumChildWindows(w['handle'],lambda c,_: buttons.append(c) if win32gui.GetClassName(c)=='Button' and win32gui.GetWindowText(c)=='OK' else None,None)
        for c in buttons:
            win32gui.SendMessage(c,win32con.BM_CLICK,0,0)
print('Dismissed completed lab disconnect notices.')
