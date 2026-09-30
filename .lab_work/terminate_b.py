state=json.loads((WORK/'state.json').read_text())
assert state['images']['B']['state']=='available'
assert len(state['images']['B']['snapshots'])==2
assert (WORK/'evidence/aws/13_image_b_available.png').exists()
page.bring_to_front()
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId='+state['instances']['B']['id'])
page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.get_by_role('heading',name='Instance summary for '+state['instances']['B']['id']+' (Instance-B-Hamdan)',exact=True).wait_for()
page.wait_for_timeout(900)
f.get_by_role('button',name='Instance state',exact=True).first.click()
f.get_by_role('menuitem',name='Terminate (delete) instance',exact=True).click()
d=f.get_by_role('dialog',name='Terminate (delete) instance',exact=True)
assert state['instances']['B']['id']+' (Instance-B-Hamdan)' in d.inner_text()
d.get_by_role('button',name='Terminate (delete)',exact=True).click()
state['instances']['B']['termination_requested']=True
(WORK/'state.json').write_text(json.dumps(state,indent=2))
print('Instance B termination requested after verifying Image B available.')
