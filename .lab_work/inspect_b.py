p=next(p for p in context.pages if 'i-0697cd44b881f1b12' in p.url)
p.bring_to_front()
f=p.frame(name='compute-react-frame')
print(f.locator('body').aria_snapshot()[:13000])
