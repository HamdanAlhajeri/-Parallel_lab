import re
state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='compute-react-frame')
checked=f.get_by_role('checkbox').evaluate_all('(els)=>els.filter(e=>e.checked).map(e=>e.getAttribute("aria-label"))')
assert set(re.findall(r'ami-[a-f0-9]+',' '.join(checked)))=={i['id'] for i in state['images'].values()}
f.get_by_role('button',name='Actions',exact=True).first.click()
f.get_by_role('menuitem',name='Deregister AMI',exact=True).last.click()
print(f.get_by_role('dialog').aria_snapshot())
