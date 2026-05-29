"""
TradeMap login using a PERSISTENT Playwright browser profile.

Why persistent profile: TradeMap aggressively bot-detects. Injecting cookies
into a fresh context causes ASP.NET cookie-detection redirect loops. A real
on-disk browser profile holds the session exactly like normal Chrome —
no cookie juggling, survives restarts, and only needs CAPTCHA solved once.

Run this once (a browser window opens):
    python scripts/trademap_login.py

It logs you in, you solve the CAPTCHA if shown, and the session is saved to
data_sources/trademap/browser_profile/ (gitignored). After that,
trademap_fetch.py reuses the profile with no further login needed for ~weeks.

Credentials come from .env (gitignored):
    TRADEMAP_EMAIL=...
    TRADEMAP_PASSWORD=...
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR    = Path(__file__).parent.parent
PROFILE_DIR = BASE_DIR / "data_sources" / "trademap" / "browser_profile"
ENV_FILE    = BASE_DIR / ".env"
INDEX_URL   = "https://www.trademap.org/Index.aspx"


def load_credentials():
    if not ENV_FILE.exists():
        print(f"ERROR: .env not found at {ENV_FILE}")
        sys.exit(1)
    creds = {}
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                creds[k.strip()] = v.strip()
    email, pwd = creds.get("TRADEMAP_EMAIL"), creds.get("TRADEMAP_PASSWORD")
    if not email or not pwd:
        print("ERROR: TRADEMAP_EMAIL and TRADEMAP_PASSWORD must be set in .env")
        sys.exit(1)
    return email, pwd


def is_logged_in(page):
    """Return True if the page shows a logged-in TradeMap session."""
    try:
        html = page.content().lower()
    except Exception:
        return False
    return ("logout" in html or "log out" in html or "myaccount" in html)


def login(headless=False):
    from playwright.sync_api import sync_playwright

    email, password = load_credentials()
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/148.0.0.0 Safari/537.36"),
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print("  Opening TradeMap ...")
        page.goto(INDEX_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Already logged in from a previous profile session?
        if is_logged_in(page):
            print("  Already logged in (profile session still valid).")
            ctx.close()
            return True

        # Click Login
        try:
            page.click("a[href*='Login'], a:text('Login'), "
                       "#ctl00_Header_LoginControl_HyperLinkLogIn", timeout=10000)
        except Exception:
            pass

        print("  Entering credentials ...")
        page.wait_for_selector("input[name='Username']", timeout=20000)
        page.fill("input[name='Username']", email)
        page.wait_for_timeout(400)
        page.fill("input[name='Password']", password)
        page.wait_for_timeout(400)
        page.click("button[name='button'][value='login'], button:text('Login')",
                   timeout=10000)
        page.wait_for_load_state("domcontentloaded", timeout=30000)

        # CAPTCHA?
        if "captcha" in page.url.lower() or "captcha" in (page.title() or "").lower():
            print()
            print("  *** CAPTCHA — please solve it in the browser window ***")
            print("  Waiting up to 2 minutes ...")
            try:
                page.wait_for_url("**/trademap.org/Index.aspx**",
                                  timeout=120000, wait_until="domcontentloaded")
            except Exception:
                pass

        page.wait_for_timeout(2000)

        if "account/login" in page.url.lower():
            print("  ERROR: Login failed — check .env credentials.")
            ctx.close()
            sys.exit(1)

        print(f"  Logged in. Session saved to profile.")
        ctx.close()
        return True


if __name__ == "__main__":
    login(headless=False)
    print("Done. Profile saved — trademap_fetch.py can now run unattended.")
