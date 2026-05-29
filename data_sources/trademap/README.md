# ITC TradeMap — Data Source Setup

## Overview

This folder contains the setup for automated trade data extraction from
[ITC TradeMap](https://www.trademap.org) using session cookie replay.

## How it works

1. Solomon logs into trademap.org in Chrome
2. A cURL request is captured from Chrome DevTools (see below)
3. The Python client (`scripts/trademap_client.py`) replays that request
   with different HS codes, countries, and year ranges
4. Results are saved as CSVs in `data/trademap/`

## Files

| File | Purpose |
|---|---|
| `sample_request.sh` | Reference cURL (cookies redacted — do not commit real cookies) |
| `hs_codes.md` | HS codes used per value chain |
| `cookies.json` | Your live session cookies — **NEVER commit this file** |

## How to refresh cookies (when session expires)

1. Log into trademap.org in Chrome
2. Open DevTools (F12) → Application tab → Cookies → trademap.org
3. Export cookies using the EditThisCookie Chrome extension, or
4. Re-run the sample query, copy as cURL, and extract the cookie header
5. Update `data_sources/trademap/cookies.json` locally

## Running the client

```bash
python scripts/trademap_client.py --hs 7403 --country UGA --years 2021-2025
```

Output CSV will be saved to `data/trademap/UGA_7403_2021_2025.csv`
