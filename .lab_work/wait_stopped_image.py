import time
for attempt in range(4):
    page.reload()
    page.locator('#compute-react-frame').wait_for(state='attached')
    f = page.frame(name='compute-react-frame')
    f.get_by_role('button',name='Instance state',exact=True).first.wait_for()
    body = f.locator('body').inner_text()
    if '\nStopped\n' in body:
        f.get_by_role('button',name='Actions',exact=True).first.click()
        f.get_by_role('menuitem',name='Image and templates',exact=True).click()
        f.get_by_role('menuitem',name='Create image',exact=True).click()
        print('IMAGE FORM:', f.locator('body').aria_snapshot()[-18000:])
        break
    print('Instance is still stopping.',flush=True)
    if attempt < 3:
        time.sleep(10)
