print('SHELL:', page.locator('body').inner_text()[:8500])
print('FRAMES:', [(f.name, f.url.split('?')[0]) for f in page.frames])
for f in page.frames[1:]:
    if f.name in ['compute-react-frame', 'instance-lx-react-frame']:
        print('FRAME:', f.name, f.locator('body').inner_text()[:15000])
