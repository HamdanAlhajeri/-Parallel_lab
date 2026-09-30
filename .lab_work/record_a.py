page = next(p for p in context.pages if '#InstanceDetails:' in p.url)
page.bring_to_front()
f = page.frame(name='compute-react-frame')
state_path = WORK / 'state.json'
state = json.loads(state_path.read_text())
state['instances']['A'].update({'public_ip':'100.54.14.202', 'public_dns':'ec2-100-54-14-202.compute-1.amazonaws.com', 'private_ip':'172.31.8.156', 'subnet':'subnet-06d969874bc72855f'})
state_path.write_text(json.dumps(state, indent=2))
for kind in ['aws','remote']:
    (WORK / 'evidence' / kind).mkdir(exist_ok=True)
page.set_viewport_size({'width':1600,'height':1000})
page.screenshot(path=str(WORK / 'evidence/aws/01_instance_a_running.png'))
for tab in ['Security','Storage','Networking']:
    f.get_by_role('tab', name=tab, exact=True).click()
    print(tab.upper(),f.get_by_role('tabpanel',name=tab,exact=True).inner_text()[:8500])
f.get_by_role('button',name='Actions',exact=True).first.click()
f.get_by_role('menuitem',name='Monitor and troubleshoot',exact=True).click()
f.get_by_role('menuitem',name='Get system log',exact=True).click()
page.wait_for_timeout(1500)
print('TABS:',[(p.url.split('#')[-1]) for p in context.pages])
