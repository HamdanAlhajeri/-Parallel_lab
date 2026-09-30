from datetime import datetime, timezone
state_path = WORK / 'state.json'
state = json.loads(state_path.read_text())
assert not state['instances'] and not state.get('launch_a_requested')
assert state['account_id'] in page.locator('body').inner_text()
f = page.frame(name='instance-lx-react-frame')
assert f.get_by_role('textbox', name='Name', exact=True).input_value() == 'Instance-A-Hamdan'
assert f.get_by_role('spinbutton', name='Number of instances', exact=True).input_value() == '1'
state['launch_a_requested'] = datetime.now(timezone.utc).isoformat()
state_path.write_text(json.dumps(state, indent=2))
f.get_by_role('button', name='Launch instance', exact=True).click()
page.wait_for_timeout(2500)
print(f.locator('body').inner_text()[:11000])
