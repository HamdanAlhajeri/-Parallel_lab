for w in rdp_windows():
    if w['class']=='#32770':
        fields=[]
        win32gui.EnumChildWindows(w['handle'],lambda c,_: fields.append({'handle':c,'class':win32gui.GetClassName(c),'text':win32gui.GetWindowText(c)}) if win32gui.GetClassName(c) in ['Static','Button'] else None,None)
        print(json.dumps({'window':w,'fields':fields}))
