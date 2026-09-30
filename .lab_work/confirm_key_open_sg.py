state=json.loads((WORK/'state.json').read_text())
f=page.frame(name='compute-react-frame')
d=f.get_by_role('dialog')
assert state['key_pair'] in d.inner_text()
d.get_by_role('textbox',name='Delete',exact=True).fill('Delete')
d.get_by_role('button',name='Delete',exact=True).click()
page.wait_for_timeout(1000)
f.get_by_role('button',name='Refresh key pairs',exact=True).click()
page.wait_for_timeout(800)
assert f.get_by_role('row').filter(has_text=state['key_pair']).count()==0
state['cleanup']['key_pair_absent']=True
page.screenshot(path=str(WORK/'evidence/aws/cleanup_key_pair.png'))
(WORK/'state.json').write_text(json.dumps(state,indent=2))
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#SecurityGroups:')
page.wait_for_timeout(1800)
print([(fr.name,fr.url[:100]) for fr in page.frames])
for fr in page.frames:
 if fr.name in ['compute-react-frame','networking-react-frame']:
  print(fr.name,fr.locator('body').aria_snapshot()[:16000])
