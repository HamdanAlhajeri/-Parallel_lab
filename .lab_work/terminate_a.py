state=json.loads((WORK/'state.json').read_text())
assert state['images']['A']['state']=='available'
assert (WORK/'evidence/aws/03_image_a_available.png').exists()
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId='+state['instances']['A']['id'])
page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.get_by_role('button',name='Instance state',exact=True).first.click()
f.get_by_role('menuitem',name='Terminate (delete) instance',exact=True).click()
print(f.get_by_role('dialog').aria_snapshot())
