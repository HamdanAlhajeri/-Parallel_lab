import re
import socket
import ssl
import hashlib
letter=sys.argv[2]
state_path=WORK/'state.json'
state=json.loads(state_path.read_text())
instance=state['instances'][letter]
page=next(p for p in context.pages if '#InstanceAudit:' in p.url and instance['id'] in p.url)
assert instance['id'] in page.url
page.reload()
page.locator('#compute-react-frame').wait_for(state='attached')
f=page.frame(name='compute-react-frame')
f.wait_for_function("() => document.body.innerText.includes('RDPCERTIFICATE') || Array.from(document.querySelectorAll('textarea')).some(e => e.value.includes('RDPCERTIFICATE'))",timeout=25000)
text=f.locator('body').inner_text()
for box in f.locator('textarea').all():
    text+='\n'+box.input_value()
matches=re.findall(r'RDPCERTIFICATE-THUMBPRINT:\s*([A-Fa-f0-9]+)',text)
assert matches, 'Certificate not yet available in AWS system log'
raw=socket.create_connection((instance['public_ip'],3389),timeout=10)
raw.sendall(bytes.fromhex('030000130ee000000000000100080003000000'))
raw.recv(1024)
tls=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
tls.check_hostname=False
tls.verify_mode=ssl.CERT_NONE
with tls.wrap_socket(raw,server_hostname=instance['public_dns']) as conn:
    fingerprint=hashlib.sha1(conn.getpeercert(binary_form=True)).hexdigest().upper()
assert fingerprint==matches[-1].upper(), 'Certificate mismatch'
instance['certificate_sha1']=fingerprint
instance['certificate_verified']=True
state_path.write_text(json.dumps(state,indent=2))
print('Instance-'+letter+' RDP certificate verified against AWS system log.')
