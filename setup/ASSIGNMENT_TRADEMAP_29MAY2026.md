# Solomon's Next Assignment: Connect Claude to ITC TradeMap

**Assigned:** 2026-05-29
**Owner:** Solomon Ariho
**Reviewer:** Hillary Arinda
**Approver:** Jerome Nuwabaasa
**Due:** 2026-06-02

## Objective

Build a way for Claude inside this repo to pull live trade data from [ITC TradeMap](https://www.trademap.org) using Solomon's logged-in account, so that data collection for the remaining six value chains stops being a manual click-through exercise.

## Why This Matters

The 6 chains still to analyse (Textiles & Garments, Pharmaceuticals, Petrochemicals & Fertilizers, Sugar & Confectionery, Plastics & Packaging, Cement & Building Materials) all need:

- Export and import volumes at HS code level
- Partner country breakdowns
- Time series (5 to 10 years)
- Unit values and trade balances

Without automation, this is dozens of manual TradeMap queries per chain. With automation, Claude pulls HS-code-level data on demand and feeds it straight into the diagnostic analysis chapters. This is the difference between weeks and days of work.

## Approach Options (ranked easiest to hardest)

### Option A: Session cookie replay (recommended, fastest)

1. Solomon logs into trademap.org in Chrome.
2. Opens DevTools, Network tab.
3. Runs one real query, e.g. **copper unwrought (HS 7403), exports from Uganda, last 5 years, all partner countries**.
4. Right-clicks the data XHR request, "Copy as cURL (bash)".
5. Pastes the cURL into the repo as a reference file.
6. Claude writes a small Python client using `requests` that:
   - Loads cookies from a local `cookies.json` file (gitignored, never committed).
   - Replays the same headers and parameters with HS code, country, and year range as variables.
   - Returns clean CSV that the chapter analyses can consume.
7. Solomon re-exports cookies every few weeks when the session expires.

**Pros:** simplest, no extra dependencies, easy to debug.
**Cons:** session breaks when Solomon logs out. TradeMap may rate-limit or change endpoints.

### Option B: Playwright with persistent browser profile

1. Install Playwright Python.
2. Use a persistent browser context that stores Solomon's logged-in session on disk.
3. Solomon logs in once interactively; the profile persists.
4. Claude drives the browser to navigate and scrape data tables, then parses HTML or downloads CSV exports.

**Pros:** survives session expiry through periodic re-login. Resilient to API changes.
**Cons:** heavier setup, slower, depends on UI not changing.

### Option C: Official ITC API (check first)

TradeMap and ITC offer an API for institutional subscribers. Worth a 10-minute check whether MTIC has a subscription tier that grants API access. If yes, this is the cleanest path: bearer token, documented endpoints, no scraping.

**Action:** Solomon asks Jerome whether MTIC has an ITC institutional account with API access. If yes, jump to Option C and skip A and B.

## Recommended Path

Default to **Option A** unless Jerome confirms an institutional API subscription. The session cookie replay approach matches the technical level of the team, ships fastest, and is good enough to get data flowing.

## Concrete First Step

1. Log into trademap.org with your account.
2. Run the test query: **copper unwrought (HS 7403), exports from Uganda, last 5 years (2021 to 2025), all partner countries**.
3. Open Chrome DevTools, switch to the Network tab, and refresh the data view.
4. Find the XHR request that returned the data table (usually the largest JSON or AJAX response).
5. Right-click it, select **Copy** then **Copy as cURL (bash)**.
6. Create a new folder in the repo: `data_sources/trademap/`.
7. Paste the cURL into `data_sources/trademap/sample_request.sh`.
8. Add `cookies.json` and any `.env` files to `.gitignore` (the cURL will contain your session cookie; do not commit raw cookies to the repo).
9. Push the branch and open a PR titled "TradeMap: capture sample request for live data integration".

Once that PR is open, Claude can take over: build a parameterised Python client, write tests, and start pulling data for every chain.

## Deliverable

By 2026-06-02, the repo should contain:

- `data_sources/trademap/sample_request.sh` (the raw cURL, scrubbed of cookies)
- `scripts/trademap_client.py` (Claude-written Python client)
- `scripts/test_trademap_client.py` (tests against three HS codes: copper 7403, iron & steel 7208, an automotive code such as 8703)
- `data/trademap/` folder with the first batch of pulled CSVs
- A `.gitignore` rule excluding `cookies.json` and `.env`
- A short README in `data_sources/trademap/README.md` explaining how to refresh cookies when the session expires

## Working Process for Solomon

1. Read this assignment in full before starting.
2. Read the meeting minutes (`setup/MEETING_MINUTES_29MAY2026.md`) for context.
3. Confirm with Jerome whether MTIC has an ITC API subscription. This decides Option A vs Option C.
4. Capture the sample cURL request as described above.
5. Hand off to Claude in this repo. Tell Claude: "Read `setup/MEETING_MINUTES_29MAY2026.md` and `setup/ASSIGNMENT_TRADEMAP_29MAY2026.md`. Then build the TradeMap client per the assignment."
6. Review what Claude produces, test it, push and open a PR.

## Important Notes

- **Never commit cookies or session tokens to the repo.** Cookies go in `cookies.json` which is gitignored. The `sample_request.sh` should have the cookie header redacted before commit.
- **Do not scrape aggressively.** Throttle requests. TradeMap is a public-good resource. One request per second or slower.
- **If TradeMap blocks the session**, Solomon must log in again, re-export cookies, and update the local file. This is normal operations, not a failure.
- **Document any HS codes used** in `data_sources/trademap/hs_codes.md` so chapter authors know which codes map to which value chain.

## Success Criterion

Claude in this repo can be asked "pull last 5 years of Uganda exports for HS 7403 to all partner countries" and produce a CSV in `data/trademap/` ready for analysis in Chapter 4 (or any other chapter).
