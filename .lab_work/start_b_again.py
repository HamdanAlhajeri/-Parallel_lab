page=next(p for p in context.pages if '#InstanceDetails:instanceId=i-0697cd44b881f1b12' in p.url)
page.bring_to_front()
f=page.frame(name='compute-react-frame')
assert '\nStopped\n' in f.locator('body').inner_text()
f.get_by_role('button',name='Instance state',exact=True).first.click()
f.get_by_role('menuitem',name='Start instance',exact=True).click()
page.wait_for_timeout(1400)
print(f.locator('body').inner_text()[:1600])
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
state['volumes']['Storage-A']['attached_to']=state['instances']['B']['id']
state['volumes']['Storage-A']['device']='xvdf'
state['instances']['B']['public_ip_before_restart']=state['instances']['B']['public_ip']
state['instances']['B']['certificate_verified']=False
state_path.write_text(json.dumps(state,indent=2))
