print('URL',page.url)
for f in page.frames:
 if f.name in ['compute-react-frame','storage-react-frame','instance-lx-react-frame']:
  print(f.name,f.locator('body').aria_snapshot()[:24000])
