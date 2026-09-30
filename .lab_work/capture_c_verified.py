h=next(w['handle'] for w in rdp_windows() if w['class']=='TscShellContainerClass' and 'Hamdan-Lab3-C' in w['title'])
focus(h)
root=Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/work')
screenshot(h,str(root/'evidence/remote/instance_c_file_contents.png'))
win32api.keybd_event(win32con.VK_LWIN,0,0,0)
win32api.keybd_event(ord('D'),0,0,0)
time.sleep(.15)
win32api.keybd_event(ord('D'),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_LWIN,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(1)
screenshot(h,str(root/'evidence/remote/15_instance_c_software.png'))
state=json.loads((root/'state.json').read_text())
state['file']['verified_on_C']=True
state['instances']['C']['data_volume']='vol-01147b8d87f5f717f'
state['instances']['C']['root_volume']='vol-041b7e0ac1da176e8'
state['instances']['C']['data_disk_automatic']=True
state['instances']['C']['drive_letter']='E'
(root/'state.json').write_text(json.dumps(state,indent=2))
print('Saved verified file contents and application icons; restored data disk was immediately usable as E:.')
