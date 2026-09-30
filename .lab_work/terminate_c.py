state=json.loads((WORK/'state.json').read_text())
assert state['file']['verified_on_C'] is True
for file in ['15_instance_c_software.png','16_instance_c_restored_file.png','instance_c_file_contents.png']:
 assert (WORK/'evidence/remote'/file).exists()
page.bring_to_front()
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId='+state['instances']['C']['id'])
page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.get_by_role('heading',name='Instance summary for '+state['instances']['C']['id']+' (Instance-C-Hamdan)',exact=True).wait_for()
page.wait_for_timeout(800)
f.get_by_role('button',name='Instance state',exact=True).first.click()
f.get_by_role('menuitem',name='Terminate (delete) instance',exact=True).click()
d=f.get_by_role('dialog',name='Terminate (delete) instance',exact=True)
assert state['instances']['C']['id']+' (Instance-C-Hamdan)' in d.inner_text()
d.get_by_role('button',name='Terminate (delete)',exact=True).click()
state['instances']['C']['termination_requested']=True
(WORK/'state.json').write_text(json.dumps(state,indent=2))
print('Instance C termination requested after all restore evidence was saved.')
