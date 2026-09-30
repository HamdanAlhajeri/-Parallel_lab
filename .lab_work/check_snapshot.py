from urllib.parse import urljoin
p=next((p for p in context.pages if '#Snapshots' in p.url),None)
if p is None:
    target=page.get_by_role('link',name='Snapshots',exact=True).get_attribute('href')
    p=context.new_page()
    p.goto(urljoin(page.url,target))
p.locator('#storage-react-frame').wait_for(state='attached')
f=p.frame(name='storage-react-frame')
f.get_by_role('button',name='Refresh snapshots',exact=True).click()
p.wait_for_timeout(1200)
print(f.get_by_role('grid',name='Snapshots',exact=True).inner_text()[:5000])
