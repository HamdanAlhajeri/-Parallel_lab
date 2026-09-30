import re
f=page.frame(name='instance-lx-react-frame')
f.get_by_role('textbox',name='Name',exact=True).fill('Instance-B-Hamdan')
f.get_by_role('button',name='Key pair name - required Select',exact=True).click()
f.get_by_role('option',name=re.compile('Hamdan-Lab3-20260925')).click()
f.get_by_role('radio',name='Select existing security group',exact=True).check()
print(f.get_by_role('group',name='Network settings',exact=True).aria_snapshot())
