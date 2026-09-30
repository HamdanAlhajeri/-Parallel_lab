state=json.loads((WORK/'state.json').read_text())
assert state['cleanup']['instances_terminated']
f=page.frame(name='compute-react-frame')
f.get_by_role('checkbox',name='Select key pair: '+state['key_pair'],exact=True).check()
f.get_by_role('button',name='Actions',exact=True).click()
f.get_by_role('menuitem',name='Delete',exact=True).last.click()
print(f.get_by_role('dialog').aria_snapshot())
