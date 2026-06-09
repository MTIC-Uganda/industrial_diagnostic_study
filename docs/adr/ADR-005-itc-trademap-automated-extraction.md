# ADR-005: ITC TradeMap Automated Data Extraction Client

## Status: Accepted

## Context

Market sizing and trade flow data for 9 value chains required pulling commodity-level export/import statistics from ITC TradeMap (intracen.org). Manual lookup and copy-paste for 9 chains across multiple years was error-prone and time-consuming. TradeMap has no public API.

## Decision

A custom Python client (`scripts/trademap_fetch.py`, `scripts/trademap_login.py`) was built to automate authenticated login and structured data extraction from TradeMap. Data exports are saved to `data/` as the canonical trade statistics source for all chapters.

## Consequences

Better: reproducible, consistent data pulls; eliminates manual transcription errors; re-runnable if additional chains or years are needed.

Worse: depends on TradeMap's login flow remaining stable; if TradeMap changes its HTML structure the client will need updating.

Watch for: TradeMap rate limiting or session expiry during long extraction runs; credentials must be kept out of version control (stored in environment variables only).
