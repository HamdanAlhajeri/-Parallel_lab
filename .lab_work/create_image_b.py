state=json.loads((WORK/'state.json').read_text())
page=next(p for p in context.pages if state['instances']['B']['id'] in p.url)
page.bring_to_front()
f=page.frame(name='compute-react-frame')
assert '\nStopped\n' in f.locator('body').inner_text()
state['instances']['B']['state']='stopped'
(WORK/'state.json').write_text(json.dumps(state,indent=2))
button=f.get_by_role('button',name='Actions',exact=True).first
if button.get_attribute('aria-expanded')!='true': button.click()
print(f.locator('body').aria_snapshot()[-14000:])
