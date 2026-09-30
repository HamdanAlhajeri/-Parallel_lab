import json
import urllib.request
import websocket
targets=json.load(urllib.request.urlopen('http://127.0.0.1:9223/json/list',timeout=5))
target=next(t for t in targets if t.get('type')=='page' and 'console.aws.amazon.com/ec2/' in t.get('url',''))
sock=websocket.create_connection(target['webSocketDebuggerUrl'],suppress_origin=True,timeout=8)
sock.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':"JSON.stringify(Array.from(document.querySelectorAll('iframe')).filter(f=>f.id.includes('react-frame')).map(f=>({id:f.id,visible:!!f.offsetWidth,text:f.contentDocument?.body?.innerText?.slice(0,8000)})))",'returnByValue':True}}))
while True:
    reply=json.loads(sock.recv())
    if reply.get('id')==1:
        print(json.dumps(reply))
        break
sock.close()
