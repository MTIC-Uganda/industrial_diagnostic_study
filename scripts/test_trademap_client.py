"""
Tests for the TradeMap client.
Run: python scripts/test_trademap_client.py

Tests three HS codes: copper (7403), iron/steel (7208), automotive (8703).
Requires a valid cookies.json — will skip tests if session is expired.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from trademap_client import fetch, load_cookies, build_url, COUNTRY_CODES, OUTPUT_DIR

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PASS = "PASS"
FAIL = "FAIL"
results = []


def test(name, fn):
    try:
        fn()
        print(f"  {PASS}  {name}")
        results.append((name, True))
    except AssertionError as e:
        print(f"  {FAIL}  {name}: {e}")
        results.append((name, False))
    except Exception as e:
        print(f"  {FAIL}  {name}: {type(e).__name__}: {e}")
        results.append((name, False))


# ── Unit tests (no network) ────────────────────────────────────────────────

print("\n── Unit tests ──")

def test_country_codes():
    assert COUNTRY_CODES["UGA"] == "800"
    assert COUNTRY_CODES["KEN"] == "404"
    assert COUNTRY_CODES["all"] == ""

def test_build_url():
    url = build_url("800", "7403", "")
    assert "trademap.org" in url
    assert "7403" in url
    assert "800" in url

def test_cookies_file_exists():
    assert (BASE_DIR / "data_sources" / "trademap" / "cookies.json").exists(), \
        "cookies.json not found — capture from Chrome DevTools"

def test_cookies_has_session():
    cookies = load_cookies()
    assert "ASP.NET_SessionId" in cookies, "Missing ASP.NET_SessionId"
    assert "TradeMap.access_token" in cookies, "Missing access_token"

test("Country code mapping",    test_country_codes)
test("URL builder",             test_build_url)
test("cookies.json exists",     test_cookies_file_exists)
test("cookies.json has keys",   test_cookies_has_session)


# ── Integration tests (live network) ──────────────────────────────────────

print("\n── Integration tests (live network — requires valid session) ──")

def test_fetch_copper():
    path = fetch("7403", "UGA", "all")
    assert path is not None, "fetch returned None"
    assert Path(path).exists(), f"Output file not found: {path}"
    assert Path(path).stat().st_size > 0, "Output file is empty"

def test_fetch_iron_steel():
    path = fetch("7208", "UGA", "all")
    assert path is not None
    assert Path(path).exists()

def test_fetch_automotive():
    path = fetch("8703", "UGA", "all")
    assert path is not None
    assert Path(path).exists()

test("Fetch copper HS 7403",      test_fetch_copper)
test("Fetch iron/steel HS 7208",  test_fetch_iron_steel)
test("Fetch automotive HS 8703",  test_fetch_automotive)


# ── Summary ────────────────────────────────────────────────────────────────

passed = sum(1 for _, ok in results if ok)
total  = len(results)
print(f"\n── Results: {passed}/{total} passed ──")
if passed < total:
    print("If integration tests failed with 'Session expired', re-capture cookies from Chrome.")
sys.exit(0 if passed == total else 1)
