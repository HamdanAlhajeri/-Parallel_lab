state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
state['volumes']['Storage-A']={'id':'vol-09dd270657364dd13','name':'Storage-A-Hamdan','az':'us-east-1a','size_gib':1,'type':'gp3','iops':3000,'throughput':125}
state_path.write_text(json.dumps(state,indent=2))
p=next(p for p in context.pages if '#Volumes' in p.url)
f=p.frame(name='storage-react-frame')
p.bring_to_front()
f.get_by_role('button',name='Refresh volumes',exact=True).click()
row=f.get_by_role('row').filter(has_text='vol-09dd270657364dd13')
row.get_by_role('checkbox').check()
p.bring_to_front()
p.set_viewport_size({'width':1800,'height':1000})
p.screenshot(path=str(WORK/'evidence/aws/08_storage_a_volume.png'))
print(row.inner_text())
