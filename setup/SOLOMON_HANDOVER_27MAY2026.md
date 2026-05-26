# MTIC Industrial Diagnostic Study — Handover to Solomon
**Date: 27 May 2026**
**From: Hillary Arinda**
**To: Solomon Ariho**

---

## What Has Been Set Up For You

The full working environment is ready on GitHub at:
https://github.com/MTIC-Uganda/industrial_diagnostic_study

The repo contains:

- Both MTIC Terms of Reference in `tor/`
- Jerome's working data document in `data/`
- Two approved report structures: `report/structure-1.md` (Report 1: Iron & Steel, Copper, Automotive — 8 chapters) and `report/structure-2.md` (Report 2: Textiles + 5 others — 11 chapters)
- Chapter skeleton files in `report/chapters/` with DATA NEEDED markers to guide you
- `CLAUDE.md` — Claude reads this automatically every session so it always knows the project context

The Commissioner has approved both report structures. You can begin chapter work immediately.

---

## Your Next Steps

1. **Pull the latest main** — run `git pull` in your terminal to get the approved structures onto your machine.

2. **Choose your first chapter** — start with the value chain you have the most data for from Jerome's document (`data/value-chain-mapping-analysis-v3-jul2025.doc`). Do not start from Chapter 1 in order. Start where the data is strongest.

3. **Create a branch for each chapter** — never work directly on main. For example:
   ```
   git checkout -b chapter/report1-iron-steel
   ```

4. **Fill the chapter using Claude** — the skeleton is already there with DATA NEEDED markers. Where data is missing, leave the marker and flag it at the 8pm check-in. Jerome will provide it.

5. **When a chapter is done** — commit it and open a pull request. Hillary reviews. Once approved it merges to main and you move to the next chapter.

6. **Daily 8pm check-in** — brief meeting: what did you complete, what is blocked, who resolves it.

7. **Save your session** — at the end of every Claude session run `/save` so your MY_BRAIN wiki stays updated and Claude picks up exactly where you left off next time.

---

## Deadline: 8 June 2026

---

## Branch Naming Convention

Use this format for all your branches:

| Report | Chapter | Branch Name |
|---|---|---|
| Report 1 | Iron & Steel | `chapter/report1-iron-steel` |
| Report 1 | Copper & Allied Metals | `chapter/report1-copper` |
| Report 1 | Automotive | `chapter/report1-automotive` |
| Report 2 | Textiles & Garments | `chapter/report2-textiles` |
| Report 2 | Pharmaceuticals | `chapter/report2-pharmaceuticals` |
| Report 2 | Petrochemicals & Fertilizers | `chapter/report2-petrochemicals` |
| Report 2 | Sugar & Confectionery | `chapter/report2-sugar` |
| Report 2 | Plastics & Packaging | `chapter/report2-plastics` |
| Report 2 | Cement & Building Materials | `chapter/report2-cement` |

---

## Key Reminders

- One chapter at a time. Finish and merge before starting the next.
- Never push directly to main. Always branch and open a PR.
- DATA NEEDED markers are not errors — they are instructions to ask Jerome.
- Executive Summary (Chapter 1 in both reports) is written last, after all other chapters are done.
- Jerome's principle: Uganda must prioritize 3 to 4 products per chain, not everything. That is the analytical lens for every chapter.
