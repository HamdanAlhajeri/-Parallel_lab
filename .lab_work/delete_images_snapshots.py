import re
state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='compute-react-frame')
d=f.get_by_role('dialog',name='Deregister AMI',exact=True)
assert set(re.findall(r'ami-[a-f0-9]+',d.inner_text()))=={i['id'] for i in state['images'].values()}
assert set(re.findall(r'snap-[a-f0-9]+',d.inner_text()))=={s for i in state['images'].values() for s in i['snapshots']}
d.get_by_role('checkbox',name='Delete associated snapshots',exact=True).check()
d.get_by_role('button',name='Deregister AMI',exact=True).click()
page.wait_for_timeout(2000)
state.setdefault('cleanup',{})['image_and_snapshot_deletion_requested']=True
(WORK/'state.json').write_text(json.dumps(state,indent=2))
print(f.locator('body').inner_text()[:4500])
