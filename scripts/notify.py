#!/usr/bin/env python3
"""
Send email and WhatsApp alerts when PocketBase drift is detected.

Called from the 'Drift Check' CI job in .github/workflows/deploy.yml
after a drift PR is opened. Both channels are attempted independently --
a failure on one does not block the other, and neither crashes the CI job.

Usage:
    python scripts/notify.py "<PR URL>"

Required GitHub Secrets (add via repo Settings → Secrets → Actions):
    SMTP_USER       Gmail address to send FROM.
                    Must be a Gmail account with 2-Step Verification
                    enabled. Generate an App Password at:
                    https://myaccount.google.com/apppasswords
                    (Account → Security → 2-Step Verification → App Passwords)
    SMTP_PASS       The 16-character App Password (NOT your Gmail login password).
    TWILIO_SID      Twilio Account SID (from console.twilio.com dashboard).
    TWILIO_TOKEN    Twilio Auth Token (same page as SID).
    TWILIO_FROM     Your Twilio WhatsApp-enabled number, prefixed with "whatsapp:".
                    For the free sandbox: whatsapp:+14155238886
                    For a registered number: whatsapp:+256xxxxxxxxx
                    NOTE — sandbox requires each recipient to opt in once
                    by sending "join <keyword>" to +14155238886 on WhatsApp.
                    For production (no opt-in needed), apply for a Twilio
                    WhatsApp Sender at console.twilio.com/develop/sms/whatsapp.
"""

import base64, json, os, smtplib, sys
import urllib.request, urllib.parse, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Recipients ────────────────────────────────────────────────────────────────
# Edit directly to add or remove people. Not secrets — just contact details.

NOTIFY_EMAILS = [
    'jnuwabaasa@gmail.com',       # Jerome Nuwabaasa — MTIC client, data owner
    'arinda.hillary@gmail.com',   # Hillary Arinda   — technical advisor, CI/CD
    'arihosolomon@gmail.com',     # Solomon Ariho    — lead developer
]

NOTIFY_WHATSAPP = [
    '+256779324208',
    '+256775102684',
    '+256704695098',
]

# ── Email (Gmail SMTP) ────────────────────────────────────────────────────────

def send_email(pr_url: str, smtp_user: str, smtp_pass: str) -> None:
    subject = '⚠️ MTIC Dashboard — PocketBase data mismatch detected'
    body = f"""\
PocketBase drift detected on the MTIC Industrial Diagnostic Dashboard.

Someone may have edited a database record directly in the PocketBase admin
interface, bypassing the normal pipeline (CSV → db/pb_setup.py → PocketBase).
This can cause the live dashboard to show data that doesn't match what the
team agreed to commit.

A pull request has been opened with the exact diff — showing every value
that changed:

  {pr_url}

── WHAT TO DO ────────────────────────────────────────────────────────────────

If the change WAS intentional (e.g. a deliberate correction):
  → Merge the pull request.
    Git will update to match what is now live in PocketBase.
    No further action needed.

If the change was NOT intentional (e.g. an accidental edit):
  → Close the pull request WITHOUT merging.
  → Then run this command (needs PB_ADMIN_EMAIL + PB_ADMIN_PASSWORD):
      python scripts/restore_from_git.py
    This pushes the last committed values back into PocketBase and
    removes any record that should not be there.

── ABOUT THIS ALERT ──────────────────────────────────────────────────────────

This check runs automatically every 6 hours.
Source: .github/workflows/deploy.yml → "Drift Check" job
"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = smtp_user
    msg['To']      = ', '.join(NOTIFY_EMAILS)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, NOTIFY_EMAILS, msg.as_string())
    print(f'  Email sent to: {", ".join(NOTIFY_EMAILS)}')

# ── WhatsApp (Twilio) ─────────────────────────────────────────────────────────

def send_whatsapp(pr_url: str, twilio_sid: str, twilio_token: str,
                  twilio_from: str) -> None:
    message = (
        '⚠️ *MTIC Dashboard — PocketBase mismatch detected*\n\n'
        'A database record may have been edited directly, bypassing the '
        'normal pipeline. A PR is open showing exactly what changed.\n\n'
        f'Review: {pr_url}\n\n'
        '• *Merge the PR* to accept the change.\n'
        '• *Close it* and run `restore_from_git.py` to revert it.'
    )

    api_url = (f'https://api.twilio.com/2010-04-01/Accounts/'
               f'{twilio_sid}/Messages.json')
    auth = base64.b64encode(
        f'{twilio_sid}:{twilio_token}'.encode()
    ).decode()

    failures = []
    for number in NOTIFY_WHATSAPP:
        to = f'whatsapp:{number}'
        data = urllib.parse.urlencode({
            'From': twilio_from,
            'To':   to,
            'Body': message,
        }).encode()
        req = urllib.request.Request(
            api_url, data=data,
            headers={'Authorization': f'Basic {auth}'},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                print(f'  WhatsApp → {number}: SID {result.get("sid", "?")}')
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:200]
            failures.append(f'{number}: HTTP {e.code} — {detail}')
        except Exception as e:
            failures.append(f'{number}: {e}')

    if failures:
        for f in failures:
            print(f'  WhatsApp failed: {f}')

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    pr_url = (sys.argv[1] if len(sys.argv) > 1
              else 'https://github.com/MTIC-Uganda/industrial_diagnostic_study/pulls')

    smtp_user   = os.environ.get('SMTP_USER', '')
    smtp_pass   = os.environ.get('SMTP_PASS', '')
    twilio_sid  = os.environ.get('TWILIO_SID', '')
    twilio_token = os.environ.get('TWILIO_TOKEN', '')
    twilio_from = os.environ.get('TWILIO_FROM', '')

    print('Sending drift notifications...')

    if smtp_user and smtp_pass:
        try:
            send_email(pr_url, smtp_user, smtp_pass)
        except Exception as e:
            print(f'  Email failed (non-fatal): {e}')
    else:
        print('  Email skipped: SMTP_USER/SMTP_PASS not set in GitHub Secrets')

    if twilio_sid and twilio_token and twilio_from:
        try:
            send_whatsapp(pr_url, twilio_sid, twilio_token, twilio_from)
        except Exception as e:
            print(f'  WhatsApp failed (non-fatal): {e}')
    else:
        print('  WhatsApp skipped: TWILIO_SID/TWILIO_TOKEN/TWILIO_FROM not set')
