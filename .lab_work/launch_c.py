import re
state=json.loads((WORK/'state.json').read_text())
page=next(p for p in context.pages if '#LaunchInstances:' in p.url)
f=page.frame(name='instance-lx-react-frame')
assert 'C' not in state['instances'] and not state.get('launch_c_requested')
assert f.get_by_role('textbox',name='Name',exact=True).input_value()=='Instance-C-Hamdan'
assert f.get_by_role('spinbutton',name='Number of instances',exact=True).input_value()=='1'
body=f.locator('body').inner_text()
assert state['images']['B']['id'] in body and 't3.micro' in body and state['security_group'] in body
state['launch_c_requested']=True
(WORK/'state.json').write_text(json.dumps(state,indent=2))
f.get_by_role('button',name='Launch instance',exact=True).click()
page.wait_for_timeout(3000)
body=f.locator('body').inner_text()
print(body[:4000])
ids=list(dict.fromkeys(re.findall(r'i-[0-9a-f]{17}',body)))
if len(ids)==1:
 state['instances']['C']={'id':ids[0],'name':'Instance-C-Hamdan'}
 (WORK/'state.json').write_text(json.dumps(state,indent=2))
