p=next(p for p in context.pages if '#CreateVolume' in p.url)
f=p.frame(name='storage-react-frame')
f.get_by_role('combobox',name='Key',exact=True).fill('Name')
f.get_by_role('combobox',name='Key',exact=True).press('Tab')
f.get_by_role('combobox',name='Value - optional',exact=True).fill('Storage-A-Hamdan')
assert f.get_by_role('spinbutton',name='Size (GiB)',exact=True).input_value()=='1'
assert f.get_by_role('spinbutton',name='Volume iops',exact=True).input_value()=='3000'
assert f.get_by_role('spinbutton',name='Throughput (MiB/s)',exact=True).input_value()=='125'
assert 'us-east-1a' in f.locator('body').inner_text()
f.get_by_role('button',name='Create volume',exact=True).click()
p.wait_for_timeout(1500)
print(f.locator('body').inner_text()[:6500])
