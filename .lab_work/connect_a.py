import os
import subprocess
import win32crypt
import win32cred
state_path = WORK / 'state.json'
state = json.loads(state_path.read_text())
instance = state['instances']['A']
assert instance['certificate_verified']
secret_dir = Path(os.environ['TEMP']) / 'Codex_CloudLab_AWS_Secrets'
f = page.frame(name='compute-react-frame')
key_path = secret_dir / (state['key_pair'] + '.pem')
files = f.locator('input[type="file"]')
if files.count():
    files.first.set_input_files(str(key_path))
else:
    f.get_by_role('textbox', name='Private key contents', exact=True).fill(key_path.read_text())
f.get_by_role('button', name='Decrypt password', exact=True).click()
dialog = f.get_by_role('dialog')
label = dialog.get_by_text('Password', exact=True)
label.wait_for()
password = label.locator('..').locator(':scope > div').nth(1).inner_text().strip()
assert 12 <= len(password) <= 128 and '\n' not in password
(secret_dir / 'Lab3_password.dpapi').write_bytes(win32crypt.CryptProtectData(password.encode(), 'Lab3 temporary password', None, None, None, 0))
target = 'TERMSRV/' + instance['public_dns']
win32cred.CredWrite({'Type': win32cred.CRED_TYPE_GENERIC, 'TargetName': target, 'UserName':'Administrator', 'CredentialBlob':password, 'Persist':win32cred.CRED_PERSIST_SESSION},0)
state.setdefault('rdp_credentials', []).append(target)
rdp = secret_dir / 'Hamdan-Lab3-A.rdp'
settings = {'full address:s':instance['public_dns'], 'username:s':'Administrator', 'screen mode id:i':'1', 'desktopwidth:i':'1440', 'desktopheight:i':'900', 'session bpp:i':'32', 'use multimon:i':'0', 'redirectclipboard:i':'1', 'redirectprinters:i':'0', 'drivestoredirect:s':'', 'keyboardhook:i':'1', 'disable wallpaper:i':'0', 'allow font smoothing:i':'1', 'authentication level:i':'2', 'prompt for credentials:i':'0', 'enablecredsspsupport:i':'1'}
rdp.write_text('\n'.join(k+':'+v for k,v in settings.items())+'\n', encoding='utf-16')
state_path.write_text(json.dumps(state, indent=2))
dialog.get_by_role('button',name='OK',exact=True).click()
del password
subprocess.Popen(['mstsc.exe',str(rdp)])
print('Windows credential stored securely; RDP launched for Instance-A.')
