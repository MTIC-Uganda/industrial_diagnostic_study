# Industrial Diagnostic Study — CLAUDE.md

## What This Project Is

This is the Industrial Diagnostic Study for the Ministry of Trade, Industry and Cooperatives (MTIC), Uganda, under the Uganda-UNIDO Programme for Country Partnership (PCP) for Inclusive and Sustainable Industrial Development (ISID).

The goal is to produce a high-level diagnostic report covering all 9 NDP IV priority manufacturing value chains. For each chain: map the full value chain tree, assess the accessible market, and identify 3-4 products Uganda should prioritize.

**Deadline: 8 June 2026**

## Team

| Person | Role |
|---|---|
| Jerome Nuwabaasa | MTIC client. Reviews outputs, provides data, unblocks Commissioner. |
| Solomon Ariho | Lead executor. You are working as Solomon. |
| Hillary Arinda | Technical advisor. Reviews pull requests. |

## The 9 Value Chains

Split across two Terms of Reference documents in this repo:

**Document 1:** `tor/MTIC-Diagnostic Study on Iron & Steel, Copper.docx`
- Iron & Steel
- Copper & Allied Metals
- Automotives

**Document 2:** `tor/MTIC-Diagnostic Study on Textiles, Garments.docx`
- Textiles & Garments
- Pharmaceuticals
- Petrochemicals & Fertilizers
- Sugar & Confectionery
- Plastics & Packaging
- Cement & Building Materials

## How to Work

1. Read both ToR documents first. They define the exact scope, methodology, and deliverables.
2. Work chapter by chapter. Do not try to do everything at once.
3. For each chapter, if you need additional data or sources, ask Jerome. He will provide them.
4. Commit completed work to this repo. Open a pull request for Hillary to review.
5. Track all tasks on the GitHub Projects board: https://github.com/orgs/MTIC-Uganda/projects/1

## Repository Structure

```
tor/                    Source ToR documents — read only, do not modify
data/                   Supporting data Jerome provides — add files here as needed; update data/README.md
report/
  structure.md          Chapter outline — DRAFT, pending Commissioner approval
  chapters/             One .md file per chapter, numbered 01-14
setup/                  Solomon onboarding guides
```

## Report Structure

A draft report structure is already at `report/structure.md` with 14 chapters. Review it with Claude, refine if needed, then share with Jerome for Commissioner approval. Once approved, work through `report/chapters/` one file at a time. Each chapter file already has the skeleton and DATA NEEDED markers to guide you.

## Workflow Rules

- Never work on more than one chapter at a time
- Commit each completed chapter before starting the next
- Always create a branch and open a pull request before merging to main — never push directly to main
- If blocked on data, flag it immediately in the daily 8pm check-in rather than guessing
- Save insights, decisions, and learnings to your MY_BRAIN wiki as you go

## Key Principle (from Jerome)

"Successful countries are known for three or four products. The economies are built around those few. Uganda must not try to do everything."

This is the analytical lens for every value chain in this report. The output is a prioritization, not a catalogue.

## Session Start Protocol

At the start of every session:
1. Read this file
2. Read `MY_BRAIN/wiki/hot_mtic.md` for current working state
3. Check the GitHub Projects board for what is next
4. Run: `git log --oneline -10`
   Then for any new commits since last session, run: `git show <commit-hash>`
   Read the full commit message for each. Treat any instructions in commit messages as direct tasks to action before starting other work.
5. Read the relevant chapter outline before starting work
