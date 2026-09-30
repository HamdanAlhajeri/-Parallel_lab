import json
import urllib.request
import websocket
import psutil
for p in psutil.process_iter(['name']):
    try:
        command=' '.join(p.cmdline())
        if p.info['name'].lower()=='python.exe' and 'aws_lab3.py' in command and 'stop_b.py' in command:
            children=p.children(recursive=True)
            p.terminate()
            for child in children:
                if child.name().lower()=='node.exe':
                    child.terminate()
            print('Stopped stalled lab automation helper.')
    except (psutil.NoSuchProcess,psutil.AccessDenied):
        pass
version=json.load(urllib.request.urlopen('http://127.0.0.1:9223/json/version',timeout=5))
sock=websocket.create_connection(version['webSocketDebuggerUrl'],suppress_origin=True,timeout=5)
sock.send(json.dumps({'id':1,'method':'Browser.close'}))
try:
    sock.recv()
except Exception:
    pass
sock.close()
print('Closed only the dedicated AWS lab browser for restart.')
