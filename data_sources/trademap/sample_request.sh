#!/bin/bash
# Sample TradeMap cURL request — cookies REDACTED
# Original query: Uganda (800), all products, all partners, bilateral time series
#
# TO UPDATE: log in, run any query, DevTools > Network > Copy as cURL (bash)
# Then replace the -b cookie string below with [REDACTED] before committing.

curl 'https://www.trademap.org/Bilateral_TS.aspx?nvpm=1%7c800%7c%7c000%7c%7cTOTAL%7c%7c%7c2%7c1%7c1%7c1%7c2%7c1%7c1%7c1%7c%7c1' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'referer: https://www.trademap.org/Index.aspx' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  -b '[REDACTED — load from data_sources/trademap/cookies.json]'

# URL parameter reference (nvpm decoded):
#   Position 2: reporter country code (800 = Uganda)
#   Position 3: partner country code (empty = all)
#   Position 4: HS product code (000 = all, 7403 = copper, 7208 = iron/steel)
#
# Country codes: UGA=800, KEN=404, TZA=834, RWA=646, COD=180, all=000
