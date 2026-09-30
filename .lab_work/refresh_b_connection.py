import re
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
page=next(p for p in context.pages if '#InstanceDetails:instanceId=i-0697cd44b881f1b12' in p.url)
page.bring_to_front()
f=page.frame(name='compute-react-frame')
f.get_by_role('button',name='Refresh instances',exact=True).click()
page.wait_for_timeout(1500)
body=f.locator('body').inner_text()
assert '\nRunning\n' in body, 'Wait for B to restart'
state['instances']['B']['public_ip']=re.search(r'Public IPv4 address\n([^\s|]+)',body).group(1)
state['instances']['B']['public_dns']=re.search(r'Public DNS\n([^\s|]+)',body).group(1)
state_path.write_text(json.dumps(state,indent=2))
print('New B address:',state['instances']['B']['public_dns'])
f.get_by_role('button',name='Actions',exact=True).first.click()
f.get_by_role('menuitem',name='Monitor and troubleshoot',exact=True).click()
f.get_by_role('menuitem',name='Get system log',exact=True).click()
