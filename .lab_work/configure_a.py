import os
import re
assert '731776047103' in page.locator('body').inner_text()
f = page.frame(name='instance-lx-react-frame')
f.get_by_role('checkbox', name='Allow RDP traffic from', exact=True).wait_for()
f.get_by_role('button', name='Anywhere 0.0.0.0/0', exact=True).click()
option = f.get_by_role('option', name=re.compile('^My IP '))
rdp_source = option.inner_text()
option.click()
f.get_by_role('button', name='Create new key pair', exact=True).click()
dialog = f.get_by_role('dialog', name='Create key pair')
key_name = 'Hamdan-Lab3-20260925'
dialog.get_by_role('textbox', name='Key pair name', exact=True).fill(key_name)
secret_dir = Path(os.environ['TEMP']) / 'Codex_CloudLab_AWS_Secrets'
secret_dir.mkdir(exist_ok=True)
with page.expect_download(timeout=30000) as download:
    dialog.get_by_role('button', name='Create key pair', exact=True).click()
download.value.save_as(str(secret_dir / (key_name + '.pem')))
body = f.locator('body').inner_text()
assert 'Microsoft Windows Server 2025 Base' in body and 't3.micro' in body
assert f.get_by_role('spinbutton', name='Storage size', exact=True).input_value() == '30'
assert f.get_by_role('spinbutton', name='Number of instances', exact=True).input_value() == '1'
state = {'account_id': '731776047103', 'username': 'HamdanAlhajeri2003', 'region': 'us-east-1',
         'key_pair': key_name, 'rdp_source': rdp_source, 'instances': {}, 'images': {}, 'volumes': {},
         'base_ami': 'ami-00d8aa800578d8b12', 'instance_type': 't3.micro'}
(WORK / 'state.json').write_text(json.dumps(state, indent=2))
print('CONFIGURATION:', body[-9500:])
