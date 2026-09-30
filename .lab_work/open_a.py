state = json.loads((WORK / 'state.json').read_text())
state['instances']['A'] = {'id': 'i-0060fb425d7ebcbad', 'name': 'Instance-A-Hamdan'}
(WORK / 'state.json').write_text(json.dumps(state, indent=2))
f = page.frame(name='instance-lx-react-frame')
f.get_by_role('link', name='i-0060fb425d7ebcbad', exact=True).click()
page.wait_for_timeout(1500)
print(page.frame(name='compute-react-frame').locator('body').inner_text()[:13000])
