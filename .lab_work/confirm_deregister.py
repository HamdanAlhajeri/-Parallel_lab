import re
state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='compute-react-frame')
d=f.get_by_role('dialog',name='Deregister AMI',exact=True)
assert set(re.findall(r'ami-[a-f0-9]+',d.inner_text()))=={i['id'] for i in state['images'].values()}
d.get_by_role('button',name='Associated snapshots (3)',exact=True).click()
print(d.aria_snapshot())
