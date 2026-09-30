p=next(p for p in context.pages if '#Volumes:' in p.url)
p.bring_to_front()
f=p.frame(name='storage-react-frame')
f.get_by_role('button',name='Refresh volumes',exact=True).click()
f.get_by_role('row').filter(has_text='vol-09dd270657364dd13').get_by_role('checkbox').check()
action=f.get_by_role('button',name='Actions',exact=True).first
if action.get_attribute('aria-expanded')!='true':
    action.click()
f.get_by_role('menuitem',name='Attach volume',exact=True).last.click()
p.wait_for_timeout(1200)
print(f.locator('body').aria_snapshot()[-10000:])
