w = rdp_windows()
print(json.dumps(w))
for window in w:
    if window['rect'][2] > window['rect'][0] and window['rect'][3] > window['rect'][1]:
        screenshot(window['handle'], 'C:/Users/Xxthe/Parallel_lab/.lab_work/rdp.png')
        break
