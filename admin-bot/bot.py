import os
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

WEB_HOST = os.environ.get('WEB_HOST', 'http://web:8000')
ADMIN_SESSION = os.environ.get('ADMIN_SESSION', 'ECHIDNA_ADMIN')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '15'))
VISIT_TIMEOUT_MS = int(os.environ.get('VISIT_TIMEOUT_MS', '10000'))

APP_URL = urljoin(WEB_HOST, '/applications')

def run_bot_once(playwright):
    browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context()
    host = WEB_HOST.replace('http://', '').replace('https://', '').split(':')[0]
    cookie = {
        'name': 'admin_session',
        'value': ADMIN_SESSION,
        'domain': host,
        'path': '/',
        'httpOnly': True,
        'secure': False
    }
    context.add_cookies([cookie])

    page = context.new_page()

    page.goto(APP_URL, wait_until='networkidle', timeout=10000)
    page.wait_for_timeout(VISIT_TIMEOUT_MS)

    page.close()

def main():
    with sync_playwright() as pw:
        while True:
            run_bot_once(pw)
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
