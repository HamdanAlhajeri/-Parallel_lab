"""Connect to a verified Lab 3 instance using its preserved DPAPI password."""
from pathlib import Path
import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
import tempfile


WORK = Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/work')
STATE_PATH = WORK / 'state.json'


def read_instance(state, letter):
    instance = state['instances'][letter]
    if instance.get('certificate_verified') is not True:
        raise ValueError('The instance certificate has not been verified.')
    if not re.fullmatch(r'i-[0-9a-f]+', instance['id']):
        raise ValueError('Unexpected instance ID.')
    ipaddress.IPv4Address(instance['public_ip'])
    if not re.fullmatch(r'[A-Za-z0-9.-]+', instance['public_dns']):
        raise ValueError('Unexpected public DNS name.')
    return instance


def record_credential(letter, instance, target):
    state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
    current = read_instance(state, letter)
    for field in ('id', 'public_ip', 'public_dns'):
        if current[field] != instance[field]:
            raise ValueError('Instance metadata changed during connection setup.')
    credentials = state.setdefault('rdp_credentials', [])
    if not isinstance(credentials, list):
        raise ValueError('Unexpected credential tracking format.')
    if target not in credentials:
        credentials.append(target)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', encoding='utf-8', dir=WORK,
            prefix='state-rdp-', suffix='.tmp', delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(state, output, indent=2)
            output.write('\n')
        os.replace(temporary, STATE_PATH)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('instance', type=str.upper, choices=('A', 'B', 'C'))
    parser.add_argument('--use-ip', action='store_true')
    args = parser.parse_args()
    letter = args.instance

    import win32cred
    import win32crypt

    state = json.loads(STATE_PATH.read_text(encoding='utf-8'))
    instance = read_instance(state, letter)
    secret_dir = Path(os.environ['TEMP']) / 'Codex_CloudLab_AWS_Secrets'
    encrypted = (secret_dir / 'Lab3_password.dpapi').read_bytes()
    password = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1].decode('utf-8')
    del encrypted
    address = instance['public_ip'] if args.use_ip else instance['public_dns']
    target = 'TERMSRV/' + address
    try:
        if not 12 <= len(password) <= 128 or '\n' in password or '\r' in password:
            raise ValueError('Unexpected saved password format.')
        record_credential(letter, instance, target)
        win32cred.CredWrite({
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': target,
            'UserName': 'Administrator',
            'CredentialBlob': password,
            'Persist': win32cred.CRED_PERSIST_SESSION,
        }, 0)
    finally:
        del password

    settings = {
        'full address:s': address,
        'username:s': 'Administrator',
        'screen mode id:i': '1',
        'desktopwidth:i': '1440',
        'desktopheight:i': '900',
        'session bpp:i': '32',
        'use multimon:i': '0',
        'redirectclipboard:i': '1',
        'redirectprinters:i': '0',
        'drivestoredirect:s': '',
        'keyboardhook:i': '1',
        'disable wallpaper:i': '0',
        'allow font smoothing:i': '1',
        'authentication level:i': '2',
        'prompt for credentials:i': '0',
        'enablecredsspsupport:i': '1',
    }
    rdp = secret_dir / f'Hamdan-Lab3-{letter}.rdp'
    rdp.write_text(''.join(key + ':' + value + '\n' for key, value in settings.items()), encoding='utf-16')
    subprocess.Popen(['mstsc.exe', str(rdp)])
    print(f'Preserved credential stored for this session; RDP launched for Instance-{letter}.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'RDP setup failed ({type(error).__name__}); no password was logged.', file=sys.stderr)
        sys.exit(1)
