import re
state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='storage-react-frame')
ids={state['volumes']['Storage-A']['id'],state['instances']['C']['data_volume']}
for vid in ids:
 row=f.get_by_role('row').filter(has_text=vid)
 assert 'Available' in row.inner_text()
 row.get_by_role('checkbox').check()
checked=f.get_by_role('row').filter(has=f.locator('input[type="checkbox"]:checked')).all_inner_texts()
assert set(re.findall(r'vol-[a-f0-9]+',' '.join(checked)))==ids
f.get_by_role('button',name='Actions',exact=True).first.click()
f.get_by_role('menuitem',name='Delete volume',exact=True).last.click()
print(f.get_by_role('dialog').aria_snapshot())
