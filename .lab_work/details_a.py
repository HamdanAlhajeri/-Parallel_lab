print('TABS:', [(i,p.url.split('#')[-1]) for i,p in enumerate(context.pages)])
page = next((p for p in context.pages if '#InstanceDetails:' in p.url), context.pages[-1])
page.bring_to_front()
print(page.frame(name='compute-react-frame').locator('body').inner_text()[:15000])
