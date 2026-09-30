for p in context.pages:
    print('TAB',p.url.split('#')[-1])
    if '#Snapshots' in p.url:
        print('BODY',p.locator('body').inner_text()[:6500])
        print('FRAMES',[(f.name, f.frame_element().is_visible()) for f in p.frames[1:] if f.name])
