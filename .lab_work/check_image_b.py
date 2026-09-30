import re
state=json.loads((WORK/'state.json').read_text())
page.bring_to_front()
page.set_viewport_size({'width':2000,'height':1250})
if '#Images:' not in page.url:
 page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#Images:visibility=owned-by-me')
 page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.get_by_role('button',name='Refresh AMIs',exact=True).wait_for()
f.get_by_role('button',name='Refresh AMIs',exact=True).click()
row=f.get_by_role('row').filter(has_text=state['images']['B']['id'])
row.get_by_role('checkbox').wait_for()
page.wait_for_timeout(1000)
body=row.inner_text()
print(body[:1800])
state['images']['B']['snapshots']=list(dict.fromkeys(re.findall(r'snap-[a-f0-9]+',body)))
if 'Available' in body:
 if not row.get_by_role('checkbox').is_checked(): row.get_by_role('checkbox').click()
 page.wait_for_timeout(500)
 state['images']['B']['state']='available'
 page.screenshot(path=str(WORK/'evidence/aws/13_image_b_available.png'))
(WORK/'state.json').write_text(json.dumps(state,indent=2))
