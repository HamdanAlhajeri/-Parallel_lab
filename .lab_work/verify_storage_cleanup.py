state=json.loads((WORK/'state.json').read_text())
page.bring_to_front()
f=page.frame(name='storage-react-frame')
assert 'You currently have no volumes in this region' in f.locator('body').inner_text()
page.screenshot(path=str(WORK/'evidence/aws/cleanup_volumes.png'))
state['cleanup']['volumes_absent']=True
(WORK/'state.json').write_text(json.dumps(state,indent=2))
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Snapshots:')
page.locator('#storage-react-frame').wait_for(state='attached')
f=page.frame(name='storage-react-frame')
f.get_by_role('button',name='Refresh snapshots',exact=True).wait_for()
f.get_by_role('button',name='Refresh snapshots',exact=True).click()
page.wait_for_timeout(1000)
body=f.locator('body').inner_text()
print(body[:3500])
if 'You currently have no snapshots' in body or 'No snapshots found' in body:
 state['cleanup']['snapshots_absent']=True
 page.screenshot(path=str(WORK/'evidence/aws/cleanup_snapshots.png'))
 (WORK/'state.json').write_text(json.dumps(state,indent=2))
