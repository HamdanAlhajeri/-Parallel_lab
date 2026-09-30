import re
import socket
import ssl
import hashlib
state_path = WORK / 'state.json'
state = json.loads(state_path.read_text())
state['security_group'] = 'sg-0b3f9891500dc7ecc'
state['instances']['A']['root_volume'] = 'vol-0a87781f82bbc250a'
state['instances']['A']['az'] = 'us-east-1a'
f = page.frame(name='compute-react-frame')
text = f.locator('body').inner_text()
for box in f.locator('textarea').all():
    text += '\n' + box.input_value()
print('READINESS:', [line for line in text.splitlines() if 'RDPCERTIFICATE' in line or 'Windows is' in line])
match = re.search(r'RDPCERTIFICATE-THUMBPRINT:\s*([A-Fa-f0-9]+)', text)
assert match, 'Windows certificate not yet in system log'
instance = state['instances']['A']
raw = socket.create_connection((instance['public_ip'],3389), timeout=10)
raw.sendall(bytes.fromhex('030000130ee000000000000100080003000000'))
raw.recv(1024)
tls = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
tls.check_hostname = False
tls.verify_mode = ssl.CERT_NONE
with tls.wrap_socket(raw, server_hostname=instance['public_dns']) as conn:
    fingerprint = hashlib.sha1(conn.getpeercert(binary_form=True)).hexdigest().upper()
assert fingerprint == match.group(1).upper(), 'RDP certificate mismatch'
instance['certificate_sha1'] = fingerprint
instance['certificate_verified'] = True
state_path.write_text(json.dumps(state, indent=2))
page.goto('https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#GetWindowsPassword:instanceId=' + instance['id'])
page.wait_for_timeout(1500)
print('Password page opened; certificate verified.')
