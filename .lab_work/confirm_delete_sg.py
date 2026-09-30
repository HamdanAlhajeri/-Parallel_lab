state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='security-groups-react-frame')
d=f.get_by_role('dialog',name='Delete security groups',exact=True)
print(d.aria_snapshot())
assert state['security_group'] in d.inner_text()
d.get_by_role('button',name='Delete',exact=True).click()
page.wait_for_timeout(1200)
f.get_by_role('button',name='Refresh security groups',exact=True).click()
page.wait_for_timeout(1000)
assert f.get_by_role('row').filter(has_text=state['security_group']).count()==0
state['cleanup']['security_group_absent']=True
assert all(state['cleanup'].get(x) is True for x in ['instances_terminated','amis_absent','volumes_absent','snapshots_absent','key_pair_absent','security_group_absent'])
state['cleanup']['aws_verified']=True
import datetime
state['cleanup']['verified_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(WORK/'state.json').write_text(json.dumps(state,indent=2))
page.screenshot(path=str(WORK/'evidence/aws/cleanup_security_group.png'))
print('All recorded Lab 3 AWS resources have been removed; default security group preserved.')
