import re
f=page.frame(name='compute-react-frame')
state=json.loads((WORK/'state.json').read_text())
assert 'B' not in state['images']
assert state['instances']['B']['id'] in f.locator('body').inner_text()
assert sorted(f.get_by_role('spinbutton',name='Size',exact=True).evaluate_all('(els)=>els.map(e=>e.value)'))==['1','30']
assert f.get_by_role('button',name='Device xvdf',exact=True).count()==1
f.get_by_role('textbox',name='Image name',exact=True).fill('Image-B-Hamdan')
f.get_by_role('textbox',name='Image description - optional',exact=True).fill('Lab 3 Windows apps and 1 GiB data volume with Hamdan.txt')
f.get_by_role('button',name='Create image',exact=True).click()
page.wait_for_timeout(3000)
body=f.locator('body').inner_text()
print(body[:5000])
ids=list(dict.fromkeys(re.findall(r'ami-[a-f0-9]+',body)))
newids=[i for i in ids if i!=state['images']['A']['id']]
if len(newids)==1:
 state['images']['B']={'id':newids[0],'name':'Image-B-Hamdan','state':'pending','snapshots':[]}
 (WORK/'state.json').write_text(json.dumps(state,indent=2))
