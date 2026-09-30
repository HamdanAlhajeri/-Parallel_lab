from pathlib import Path
import sys
import json

sys.dont_write_bytecode = True
ROOT = Path('C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab')
WORK = ROOT / 'Lab3/work'
sys.path.insert(0, str(ROOT / '.lab_browser'))
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

with sync_playwright() as driver:
    browser = driver.chromium.connect_over_cdp('http://127.0.0.1:9223')
    context = browser.contexts[0]
    context.set_default_timeout(12000)
    page = next((p for p in context.pages if '/ec2/' in p.url), None)
    if len(sys.argv) > 1:
        exec(Path(sys.argv[1]).read_text(encoding='utf-8'))
    else:
        print(json.dumps([{'url': p.url.split('?')[0], 'title': p.title()} for p in context.pages], indent=2))
