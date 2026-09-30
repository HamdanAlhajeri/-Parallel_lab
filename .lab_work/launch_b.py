import re
f=page.frame(name='instance-lx-react-frame')
f.get_by_role('button',name='Common security groups Select security groups',exact=True).click()
f.get_by_role('option',name=re.compile('sg-0b3f9891500dc7ecc')).click()
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
assert 'B' not in state['instances'] and not state.get('launch_b_requested')
assert f.get_by_role('textbox',name='Name',exact=True).input_value()=='Instance-B-Hamdan'
assert f.get_by_role('spinbutton',name='Number of instances',exact=True).input_value()=='1'
body=f.locator('body').inner_text()
assert 'ami-08c8483cf822da554' in body and 't3.micro' in body and 'sg-0b3f9891500dc7ecc' in body
state['launch_b_requested']=True
state_path.write_text(json.dumps(state,indent=2))
f.get_by_role('button',name='Launch instance',exact=True).click()
page.wait_for_timeout(2500)
print(f.locator('body').inner_text()[:3500])
