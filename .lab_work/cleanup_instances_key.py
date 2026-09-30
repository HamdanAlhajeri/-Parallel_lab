state=json.loads((WORK/'state.json').read_text())
page.bring_to_front()
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Instances:')
page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.get_by_role('button',name='Refresh instances',exact=True).wait_for()
f.get_by_role('button',name='Refresh instances',exact=True).click()
page.wait_for_timeout(1000)
for letter in ['B','C']:
 row=f.get_by_role('row').filter(has_text=state['instances'][letter]['id'])
 assert 'Terminated' in row.inner_text()
 state['instances'][letter]['state']='terminated'
assert state['instances']['A']['state']=='terminated'
state['cleanup']['instances_terminated']=True
page.screenshot(path=str(WORK/'evidence/aws/cleanup_instances.png'))
(WORK/'state.json').write_text(json.dumps(state,indent=2))
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#KeyPairs:')
page.locator('#compute-react-frame').wait_for(state='attached')
page.wait_for_timeout(1200)
print(f.locator('body').aria_snapshot()[:14000])
