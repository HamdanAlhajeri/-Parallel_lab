h = next(w['handle'] for w in rdp_windows() if w['class'] == '#32770')
focus(h)
buttons = []
win32gui.EnumChildWindows(h, lambda c, _: buttons.append((c,win32gui.GetWindowText(c))) if win32gui.GetClassName(c) == 'Button' else None, None)
for c,label in buttons:
    if label.replace('&','') in ['Connect','Yes']:
        win32gui.SendMessage(c, win32con.BM_CLICK, 0, 0)
        break
time.sleep(4)
print(json.dumps(rdp_windows()))
visible = [w for w in rdp_windows() if w['rect'][2] > w['rect'][0]]
if visible:
    screenshot(visible[0]['handle'], 'C:/Users/Xxthe/Parallel_lab/.lab_work/rdp.png')
