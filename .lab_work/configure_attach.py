import re
p=next(p for p in context.pages if '#AttachVolume' in p.url)
p.bring_to_front()
f=p.frame(name='storage-react-frame')
f.get_by_role('button',name='Search instance ID or name tag',exact=True).click()
print('OPTIONS',f.get_by_role('option').all_text_contents())
f.get_by_role('option',name=re.compile('i-0697cd44b881f1b12')).click()
f.get_by_role('button',name='Device name Select a device name',exact=True).click()
print('DEVICES',f.get_by_role('option').all_text_contents())
