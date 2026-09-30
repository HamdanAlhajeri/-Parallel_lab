f=page.frame(name='compute-react-frame')
d=f.get_by_role('dialog',name='Terminate (delete) instance',exact=True)
assert 'i-0060fb425d7ebcbad (Instance-A-Hamdan)' in d.inner_text()
d.get_by_role('button',name='Terminate (delete)',exact=True).click()
page.wait_for_timeout(1200)
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
state['instances']['A']['termination_requested']=True
state_path.write_text(json.dumps(state,indent=2))
print(f.locator('body').inner_text()[:1400])
