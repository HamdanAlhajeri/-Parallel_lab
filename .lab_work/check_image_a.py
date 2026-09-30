import re
f = page.frame(name='compute-react-frame')
page.bring_to_front()
f.get_by_role('button',name='Refresh AMIs',exact=True).click()
row=f.get_by_role('row').filter(has_text='ami-08c8483cf822da554')
row.get_by_role('checkbox').wait_for()
page.wait_for_timeout(1000)
text=row.inner_text()
print('Image-A:',text[:650])
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
state['images']['A']['snapshots']=list(set(re.findall(r'snap-[0-9a-f]+',text)))
if 'Available' in text:
    state['images']['A']['state']='available'
    row.get_by_role('checkbox').check()
    page.bring_to_front()
    page.screenshot(path=str(WORK/'evidence/aws/03_image_a_available.png'))
state_path.write_text(json.dumps(state,indent=2))
