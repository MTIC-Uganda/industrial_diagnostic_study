"""
TradeMap data fetcher (Playwright-driven).

Navigates TradeMap like a human using the logged-in session, drives the
product/country/trade-flow dropdowns, and scrapes the time-series table
into clean CSV. Built this way because TradeMap aggressively bot-detects
direct URL access (redirect loops), but a natural navigation flow works.

Usage:
    python scripts/trademap_fetch.py --hs 7403 --flow exports
    python scripts/trademap_fetch.py --hs 7403 --flow imports
    python scripts/trademap_fetch.py --chapter copper      # all copper HS codes

Falls back to auto-login (visible browser, you solve CAPTCHA once) if the
saved session has expired.
"""

import sys
import io
import json
import csv
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR     = Path(__file__).parent.parent
PROFILE_DIR  = BASE_DIR / "data_sources" / "trademap" / "browser_profile"
OUTPUT_DIR   = BASE_DIR / "data" / "trademap"
INDEX_URL    = "https://www.trademap.org/Index.aspx"
DATA_PAGE    = "https://www.trademap.org/Country_SelProductCountry_TS.aspx"

# HS codes grouped by value chain (4-digit)
CHAINS = {
    "iron-steel":  ["7208", "7209", "7213", "7214"],
    "copper":      ["7403", "7408", "7413"],
    "automotive":  ["8703", "8704", "8708"],
    "textiles":    ["5201", "5205", "6109", "6203"],
    "pharma":      ["3004", "3002", "2941"],
    "petrochem":   ["3102", "3105", "2710"],
    "sugar":       ["1701", "1704"],
    "plastics":    ["3920", "3923", "4819"],
    "cement":      ["2523", "6810"],
}

# Dropdown control IDs
DD_PRODUCT   = "#ctl00_NavigationControl_DropDownList_Product"
DD_TRADETYPE = "#ctl00_NavigationControl_DropDownList_TradeType"
DD_COUNTRY   = "#ctl00_NavigationControl_DropDownList_Country"
GRID         = "#ctl00_PageContent_MyGridView1"


def session_alive(page):
    """Check whether we're logged in (not bounced to login/captcha)."""
    url = page.url.lower()
    return "account/login" not in url and "captcha" not in url


def select_and_wait(page, selector, value=None, label=None):
    """Select a dropdown option and wait for the ASP.NET postback navigation
    to fully complete. These dropdowns fire __doPostBack on change, which
    reloads the whole page — so we must wait for navigation, not just settle."""
    try:
        with page.expect_navigation(timeout=30000, wait_until="domcontentloaded"):
            if label is not None:
                page.select_option(selector, label=label)
            else:
                page.select_option(selector, value=value)
    except Exception:
        # Some selects don't trigger a full navigation; ignore and settle below
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1500)  # let the grid re-render


def scrape_grid(page):
    """Read the data grid into a list of rows."""
    page.wait_for_selector(GRID, timeout=20000)
    table = page.query_selector(GRID)
    if not table:
        return None
    rows = []
    for tr in table.query_selector_all("tr"):
        cells = [td.inner_text().strip() for td in tr.query_selector_all("td, th")]
        if any(cells):
            rows.append(cells)
    return rows


def set_product(page, hs_code):
    """
    Select the HS code in the product dropdown. TradeMap shows products
    hierarchically; selecting the 2-digit chapter first reveals the 4-digit
    codes. Handles both cases.
    """
    # Try selecting the 4-digit code directly first
    opts = {o.get_attribute("value"): o.inner_text()
            for o in page.query_selector_all(f"{DD_PRODUCT} option")}
    if hs_code in opts:
        select_and_wait(page, DD_PRODUCT, value=hs_code)
        return True

    # Otherwise drill: select the 2-digit chapter, then the 4-digit code
    chapter = hs_code[:2]
    if chapter in opts:
        select_and_wait(page, DD_PRODUCT, value=chapter)
        opts2 = {o.get_attribute("value"): o.inner_text()
                 for o in page.query_selector_all(f"{DD_PRODUCT} option")}
        if hs_code in opts2:
            select_and_wait(page, DD_PRODUCT, value=hs_code)
            return True
    return False


def fetch_one(page, hs_code, flow):
    """Fetch one HS code + trade flow. Returns path to saved CSV or None."""
    flow_label = "Exports" if flow == "exports" else "Imports"
    print(f"  HS {hs_code} | {flow_label} ...")

    # Set trade flow
    select_and_wait(page, DD_TRADETYPE, label=flow_label)

    # Set product
    if not set_product(page, hs_code):
        print(f"    SKIP: HS {hs_code} not found in product dropdown")
        return None

    rows = scrape_grid(page)
    if not rows:
        print(f"    WARNING: no data table for HS {hs_code}")
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d")
    fname = f"UGA_{hs_code}_{flow}_{ts}.csv"
    fpath = OUTPUT_DIR / fname
    with open(fpath, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"    Saved -> {fname}  ({len(rows)-1} rows)")
    return fpath


def run(hs_codes, flow):
    from playwright.sync_api import sync_playwright

    if not PROFILE_DIR.exists():
        print("  No browser profile found. Run first:  python scripts/trademap_login.py")
        sys.exit(1)

    results = []
    with sync_playwright() as p:
        # Reuse the persistent logged-in profile (headless OK once logged in)
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/148.0.0.0 Safari/537.36"),
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Navigate naturally: Index first, then the data page
        print("  Loading session from profile ...")
        page.goto(INDEX_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        page.goto(DATA_PAGE, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        if not session_alive(page):
            print("  Session expired — run:  python scripts/trademap_login.py")
            ctx.close()
            sys.exit(1)

        # Ensure reporter is Uganda
        try:
            select_and_wait(page, DD_COUNTRY, label="Uganda")
        except Exception:
            pass

        for hs in hs_codes:
            try:
                r = fetch_one(page, hs, flow)
                results.append((hs, r))
            except Exception as e:
                print(f"    ERROR on HS {hs}: {type(e).__name__}: {e}")
                results.append((hs, None))
            time.sleep(2)  # throttle between codes

        ctx.close()

    ok = sum(1 for _, r in results if r)
    print(f"\n  Done: {ok}/{len(results)} HS codes fetched into data/trademap/")
    return results


def main():
    ap = argparse.ArgumentParser(description="Fetch TradeMap data (Playwright)")
    ap.add_argument("--hs", help="Single HS code, e.g. 7403")
    ap.add_argument("--chapter", choices=CHAINS.keys(),
                    help="Fetch all HS codes for a value chain")
    ap.add_argument("--flow", choices=["exports", "imports"], default="exports")
    args = ap.parse_args()

    if args.chapter:
        codes = CHAINS[args.chapter]
    elif args.hs:
        codes = [args.hs]
    else:
        ap.print_help()
        return

    run(codes, args.flow)


if __name__ == "__main__":
    main()
