import json
import urllib.request
import psutil
targets=json.load(urllib.request.urlopen('http://127.0.0.1:9223/json/list'))
for target in targets:
    url=target.get('url','')
    if target.get('type')=='page' and 'console.aws.amazon.com/ec2/' in url:
        fragment=url.split('#')[-1]
        print('Lab tab:',fragment)
        if fragment.startswith(('Snapshots:','LaunchInstances:','Volumes:')):
            urllib.request.urlopen('http://127.0.0.1:9223/json/close/'+target['id']).read()
            print('Closed completed auxiliary lab tab.')
m=psutil.virtual_memory()
print('Available memory GiB:',round(m.available/2**30,2))
