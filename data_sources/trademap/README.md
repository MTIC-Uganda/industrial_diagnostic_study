# ITC TradeMap — Automated Data Source

Pulls live trade statistics from [ITC TradeMap](https://www.trademap.org)
into clean CSVs for use in the value-chain chapters.

## How it works

A **persistent Playwright browser profile** holds your logged-in TradeMap
session on disk (like a real Chrome profile). Scripts reuse it to navigate
TradeMap, drive the product / trade-flow dropdowns, and scrape the
time-series tables. This approach is used because TradeMap aggressively
bot-detects direct API/cURL access (redirect loops); a real browser profile
behaves like a human session and is stable for weeks.

## One-time setup

1. Put your credentials in `.env` at the repo root (gitignored):
   ```
   TRADEMAP_EMAIL=your@email.com
   TRADEMAP_PASSWORD=yourpassword
   ```
2. Log in once — a browser window opens; solve the CAPTCHA if shown:
   ```
   python scripts/trademap_login.py
   ```
   The session is saved to `data_sources/trademap/browser_profile/` (gitignored).

## Fetching data

```bash
# One HS code, exports
python scripts/trademap_fetch.py --hs 7403 --flow exports

# One HS code, imports
python scripts/trademap_fetch.py --hs 7208 --flow imports

# All HS codes for a whole value chain
python scripts/trademap_fetch.py --chapter copper --flow exports
python scripts/trademap_fetch.py --chapter iron-steel --flow imports
```

Value-chain keys: `iron-steel`, `copper`, `automotive`, `textiles`,
`pharma`, `petrochem`, `sugar`, `plastics`, `cement`.

Output CSVs land in `data/trademap/`, named
`UGA_<hs>_<flow>_<date>.csv`, with one row per partner country and one
column per year (last 5 years), e.g.:

```
Exporters, Imported value in 2020, ... 2024
World,     135,322, ... 219,496
China,     25,765,  ... 103,222
Japan,     86,087,  ... 88,468
```

## When the session expires (after a few weeks)

Re-run `python scripts/trademap_login.py` and solve the CAPTCHA once.
That's the only manual step, and only occasionally.

## Files

| File | Purpose |
|---|---|
| `scripts/trademap_login.py` | One-time login → saves persistent profile |
| `scripts/trademap_fetch.py` | Fetches data (the workhorse) |
| `hs_codes.md` | HS codes mapped to each of the 9 value chains |
| `.env` | Credentials — **gitignored, never committed** |
| `browser_profile/` | Saved session — **gitignored, never committed** |
