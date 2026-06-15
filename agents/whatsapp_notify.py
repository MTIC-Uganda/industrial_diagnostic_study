#!/usr/bin/env python3
"""
MTIC WhatsApp Notification Agent

Reads data/revision/ for new revision notices and sends a WhatsApp message
to the team when a chapter fails the quality gate.

Supports two providers — set WA_PROVIDER to choose:

  WA_PROVIDER=callmebot  (default — free, no Twilio account needed)
    WA_RECIPIENT  = phone number with country code, no + (e.g. 256700123456)
    WA_TOKEN      = CallMeBot API key (get it by sending a WhatsApp message to
                    +34 644 49 78 21 with the text: "I allow callmebot to send
                    me messages". The key arrives by WhatsApp.)

  WA_PROVIDER=twilio
    WA_RECIPIENT  = full WhatsApp number (e.g. whatsapp:+256700123456)
    WA_TOKEN      = ACCOUNT_SID:AUTH_TOKEN (colon-separated)
    WA_FROM       = Twilio WhatsApp sandbox number (e.g. +14155238886)

Usage (CI — called by the review job in deploy.yml):
    python agents/whatsapp_notify.py

Usage (local test):
    python agents/whatsapp_notify.py --test
"""

import json, os, sys, textwrap, urllib.request, urllib.parse, urllib.error, argparse
from pathlib import Path

ROOT         = Path(__file__).resolve().parent.parent
REVISION_DIR = ROOT / 'data' / 'revision'

WA_PROVIDER  = os.environ.get('WA_PROVIDER', 'callmebot').lower()
WA_RECIPIENT = os.environ.get('WA_RECIPIENT', '')
WA_TOKEN     = os.environ.get('WA_TOKEN', '')
WA_FROM      = os.environ.get('WA_FROM', '')

PROD_URL     = os.environ.get('PROD_URL', 'http://89.167.121.193:8201')
GITHUB_REPO  = 'https://github.com/MTIC-Uganda/industrial_diagnostic_study'


def send_callmebot(phone: str, api_key: str, message: str):
    url = (
        'https://api.callmebot.com/whatsapp.php'
        f'?phone={urllib.parse.quote(phone)}'
        f'&text={urllib.parse.quote(message)}'
        f'&apikey={urllib.parse.quote(api_key)}'
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read().decode()
            if 'Message queued' in body or resp.status == 200:
                print(f'  WhatsApp sent via CallMeBot to {phone[:6]}***')
                return True
            print(f'  CallMeBot response: {body[:200]}')
            return False
    except urllib.error.URLError as e:
        print(f'  WARN: CallMeBot request failed: {e}')
        return False


def send_twilio(recipient: str, account_sid_token: str, from_num: str, message: str):
    try:
        sid, token = account_sid_token.split(':', 1)
    except ValueError:
        print('  ERROR: WA_TOKEN must be ACCOUNT_SID:AUTH_TOKEN for Twilio provider.')
        return False

    url  = f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json'
    data = urllib.parse.urlencode({
        'From': f'whatsapp:{from_num}' if not from_num.startswith('whatsapp:') else from_num,
        'To':   recipient if recipient.startswith('whatsapp:') else f'whatsapp:{recipient}',
        'Body': message,
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    import base64
    credentials = base64.b64encode(f'{sid}:{token}'.encode()).decode()
    req.add_header('Authorization', f'Basic {credentials}')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get('sid'):
                print(f'  WhatsApp sent via Twilio — SID: {result["sid"][:12]}…')
                return True
            print(f'  Twilio error: {result}')
            return False
    except urllib.error.URLError as e:
        print(f'  WARN: Twilio request failed: {e}')
        return False


def send(message: str) -> bool:
    if not WA_RECIPIENT or not WA_TOKEN:
        print('  WARN: WA_RECIPIENT or WA_TOKEN not set — WhatsApp notification skipped.')
        print('  Set these secrets in GitHub: WA_RECIPIENT, WA_TOKEN, WA_PROVIDER.')
        return False

    if WA_PROVIDER == 'twilio':
        return send_twilio(WA_RECIPIENT, WA_TOKEN, WA_FROM, message)
    else:
        return send_callmebot(WA_RECIPIENT, WA_TOKEN, message)


def build_message(notices: list[dict]) -> str:
    lines = [
        '🔴 *MTIC Pipeline — Revision Required*',
        '',
    ]
    for n in notices:
        lines += [
            f'*Chain:* {n["vc_name"]} ({n["vc_id"]})',
            f'*Failures:* {n["mandatory_failures"]} mandatory',
            f'*Summary:* {n["summary"][:200]}' if n.get("summary") else '',
            '',
        ]
    lines += [
        f'📊 Dashboard: {PROD_URL}',
        f'📋 Pipeline tab: {PROD_URL}/#pipeline',
        f'🔗 Repo: {GITHUB_REPO}',
        '',
        'Fix the flagged data and re-upload to data/uploads/ to re-run the pipeline.',
    ]
    return '\n'.join(l for l in lines if l is not None)


def load_revision_notices() -> list[dict]:
    notices = []
    for f in sorted(REVISION_DIR.glob('*_revision.md')):
        text = f.read_text('utf-8')
        vc_id = f.stem.replace('_revision', '')
        # Parse summary from the markdown
        summary = ''
        in_summary = False
        for line in text.splitlines():
            if line.startswith('## Summary'):
                in_summary = True
                continue
            if in_summary and line.strip() and not line.startswith('#'):
                summary = line.strip()
                break
        # Count mandatory failures (### headings before Advisories)
        mandatory = sum(1 for l in text.splitlines()
                        if l.startswith('### ') and '—' in l and 'Advisory' not in l)
        vc_name = f.stem.replace('_revision','').replace('VC0','VC0').upper()
        # Get nice name from filename
        VC_NAMES = {
            'VC01':'Iron & Steel','VC02':'Copper & Allied Metals',
            'VC03':'Automotive','VC04':'Textiles & Garments',
            'VC05':'Pharmaceuticals','VC06':'Petrochemicals & Fertilizers',
            'VC07':'Sugar & Confectionery','VC08':'Plastics & Packaging',
            'VC09':'Cement & Building Materials',
        }
        notices.append({
            'vc_id': vc_id,
            'vc_name': VC_NAMES.get(vc_id, vc_id),
            'mandatory_failures': mandatory,
            'summary': summary,
            'file': str(f.relative_to(ROOT)),
        })
    return notices


def run(test: bool = False):
    print('\n── MTIC WhatsApp Notifier ──')

    if test:
        notices = [{
            'vc_id': 'VC01',
            'vc_name': 'Iron & Steel',
            'mandatory_failures': 3,
            'summary': 'Test notification — pipeline is working.',
        }]
        print('  Sending test message…')
    else:
        notices = load_revision_notices()
        if not notices:
            print('  No revision notices found — nothing to notify.')
            return

    message = build_message(notices)
    print(f'  Message ({len(message)} chars):')
    print(textwrap.indent(message, '    '))

    success = send(message)
    if success:
        print('  Notification sent.')
    else:
        print('  Notification NOT sent — check WA_* environment variables.')
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MTIC WhatsApp Notifier')
    parser.add_argument('--test', action='store_true',
                        help='Send a test message without reading revision notices.')
    args = parser.parse_args()
    run(test=args.test)
