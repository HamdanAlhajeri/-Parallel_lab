import re
state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='storage-react-frame')
d=f.get_by_role('dialog',name='Delete 2 volumes?',exact=True)
assert set(re.findall(r'vol-[a-f0-9]+',d.inner_text()))=={state['volumes']['Storage-A']['id'],state['instances']['C']['data_volume']}
d.get_by_role('textbox',name='delete',exact=True).fill('delete')
d.get_by_role('button',name='Delete',exact=True).click()
page.wait_for_timeout(1500)
f.get_by_role('button',name='Refresh volumes',exact=True).click()
page.wait_for_timeout(1200)
print(f.locator('body').inner_text()[:3500])
