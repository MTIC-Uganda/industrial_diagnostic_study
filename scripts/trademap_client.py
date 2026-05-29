"""
ITC TradeMap data extraction client — auto-refreshing session.

The client uses your refresh token to get new access tokens automatically
whenever the session expires. You never need to log in manually again
as long as the refresh token remains valid (typically 30+ days).

Usage:
    python scripts/trademap_client.py --hs 7403
    python scripts/trademap_client.py --hs 7208 --partner KEN
    python scripts/trademap_client.py --batch          # all 9 value chains

Output CSVs go to data/trademap/.
Cookies are auto-updated in data_sources/trademap/cookies.json.
"""

import requests
import json
import csv
import sys
import time
import argparse
import base64
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR     = Path(__file__).parent.parent
COOKIES_FILE = BASE_DIR / "data_sources" / "trademap" / "cookies.json"
OUTPUT_DIR   = BASE_DIR / "data" / "trademap"
BASE_URL     = "https://www.trademap.org"
TOKEN_URL    = "https://idsrv.marketanalysis.intracen.org/connect/token"
CLIENT_ID    = "TradeMap"

COUNTRY_CODES = {
    "UGA": "800", "KEN": "404", "TZA": "834", "RWA": "646",
    "ETH": "231", "COD": "180", "SDN": "729", "SSD": "728",
    "BDI": "108", "ZMB": "894", "all": "",
}

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "referer": f"{BASE_URL}/Index.aspx",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "dnt": "1",
    "upgrade-insecure-requests": "1",
}

# ── Batch HS codes for all 9 value chains ──────────────────────────────────
BATCH_HS_CODES = {
    "Iron & Steel":              ["7208", "7209", "7213", "7214"],
    "Copper & Allied Metals":    ["7403", "7408", "7413"],
    "Automotives":               ["8703", "8704", "8708"],
    "Textiles & Garments":       ["5201", "5205", "6109", "6203"],
    "Pharmaceuticals":           ["3004", "3002", "2941"],
    "Petrochemicals/Fertilizers":["3102", "3105", "2710"],
    "Sugar & Confectionery":     ["1701", "1704"],
    "Plastics & Packaging":      ["3920", "3923", "4819"],
    "Cement & Building Materials":["2523", "6810"],
}


def load_cookies():
    if not COOKIES_FILE.exists():
        print(f"ERROR: {COOKIES_FILE} not found.")
        print("Paste a fresh cURL from Chrome DevTools to set up cookies.json.")
        sys.exit(1)
    with open(COOKIES_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_cookies(cookies):
    COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)


def decode_jwt_exp(token):
    """Return the expiry timestamp from a JWT without a crypto library."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)  # pad base64
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data.get("exp", 0)
    except Exception:
        return 0


def token_is_expired(token):
    exp = decode_jwt_exp(token)
    now = datetime.now(timezone.utc).timestamp()
    return now >= exp - 30  # 30-second buffer


def refresh_session(cookies):
    """Use the refresh token to get new access/id tokens. Updates cookies in place."""
    print("  Session expired — refreshing tokens automatically...")
    refresh_token = cookies.get("TradeMap.refresh_token")
    if not refresh_token:
        print("  ERROR: No refresh token in cookies.json. Log in manually once.")
        sys.exit(1)

    try:
        resp = requests.post(TOKEN_URL, data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "refresh_token": refresh_token,
        }, timeout=15)
    except requests.exceptions.ConnectionError:
        print("  ERROR: Cannot reach TradeMap identity server.")
        print("  Log into trademap.org in Chrome, copy a fresh cURL, and update cookies.json.")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"  ERROR: Token refresh failed ({resp.status_code}).")
        print("  Log into trademap.org in Chrome, copy a fresh cURL, and update cookies.json.")
        sys.exit(1)

    data = resp.json()
    cookies["TradeMap.access_token"]  = data["access_token"]
    cookies["TradeMap.id_token"]      = data.get("id_token", cookies.get("TradeMap.id_token", ""))
    if "refresh_token" in data:
        cookies["TradeMap.refresh_token"] = data["refresh_token"]
    save_cookies(cookies)
    print("  Tokens refreshed and saved to cookies.json.")
    return cookies


def get_valid_cookies():
    """Load cookies and refresh if the access token has expired."""
    cookies = load_cookies()
    access_token = cookies.get("TradeMap.access_token", "")
    if token_is_expired(access_token):
        cookies = refresh_session(cookies)
    return cookies


def build_url(reporter_code, hs_code="000", partner_code="", page="Bilateral_TS"):
    parts = [
        "1", reporter_code, partner_code, hs_code,
        "", "TOTAL", "", "",
        "2", "1", "1", "1", "2", "1", "1", "1", "", "1",
    ]
    nvpm = "%7c".join(parts)
    return f"{BASE_URL}/{page}.aspx?nvpm={nvpm}"


def parse_table(html):
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  ERROR: Run: pip install beautifulsoup4")
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")

    for tid in [
        "ctl00_PageContent_GridViewPartners",
        "ctl00_PageContent_GridViewProducts",
        "ctl00_PageContent_GridViewIndicators",
        "ctl00_PageContent_GridViewBilateral",
    ]:
        table = soup.find("table", {"id": tid})
        if table:
            break
    else:
        tables = soup.find_all("table")
        if not tables:
            return None, "No tables found"
        table = max(tables, key=lambda t: len(t.find_all("tr")))

    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if any(cells):
            rows.append(cells)

    return rows, None


def fetch(hs_code, reporter="UGA", partner="all"):
    """Pull trade data for one HS code. Returns path to saved CSV."""
    cookies = get_valid_cookies()
    reporter_code = COUNTRY_CODES.get(reporter.upper(), reporter)
    partner_code  = COUNTRY_CODES.get(partner.upper(), "")

    url = build_url(reporter_code, hs_code, partner_code)
    print(f"  Fetching HS {hs_code} | {reporter} -> {partner if partner != 'all' else 'all partners'}")

    time.sleep(1)  # Throttle: 1 request/second — do not remove
    resp = requests.get(url, cookies=cookies, headers=HEADERS, timeout=30,
                        allow_redirects=True)

    if resp.status_code != 200:
        print(f"  ERROR: HTTP {resp.status_code}")
        return None

    # Detect login redirect (expired session not caught by JWT check)
    if "trademap.org/Account/Login" in resp.url or \
       "ctl00_Header_LoginControl" in resp.text:
        cookies = refresh_session(cookies)
        time.sleep(1)
        resp = requests.get(url, cookies=cookies, headers=HEADERS, timeout=30)

    rows, err = parse_table(resp.text)
    if err or not rows:
        print(f"  WARNING: {err or 'Empty response'}")
        return None

    # Save CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    partner_label = partner.upper() if partner != "all" else "WORLD"
    ts = datetime.now().strftime("%Y%m%d")
    filename = f"{reporter.upper()}_{hs_code}_{partner_label}_{ts}.csv"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    print(f"  Saved -> {filepath.name}  ({len(rows)-1} rows)")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Pull trade data from ITC TradeMap (auto-refreshing session)"
    )
    parser.add_argument("--hs",       help="HS code, e.g. 7403")
    parser.add_argument("--reporter", default="UGA",
                        help="ISO3 reporter country (default: UGA)")
    parser.add_argument("--partner",  default="all",
                        help="ISO3 partner country or 'all' (default: all)")
    parser.add_argument("--batch",    action="store_true",
                        help="Pull all HS codes for all 9 value chains")
    args = parser.parse_args()

    if args.batch:
        total = sum(len(v) for v in BATCH_HS_CODES.values())
        print(f"Batch mode: {total} HS codes across 9 value chains")
        for chain, codes in BATCH_HS_CODES.items():
            print(f"\n[{chain}]")
            for hs in codes:
                fetch(hs, args.reporter, args.partner)
    elif args.hs:
        fetch(args.hs, args.reporter, args.partner)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
