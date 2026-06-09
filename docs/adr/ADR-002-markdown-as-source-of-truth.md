# ADR-002: Markdown as Source of Truth, Formatted Outputs Derived

## Status: Accepted

## Context

Reports needed to be delivered as Word (.docx) and PowerPoint (.pptx) files for MTIC. However, editing Word files directly creates risk: hand-edits can become the only copy of a change, version control is difficult, and merge conflicts on binary files are unresolvable.

## Decision

All chapter content is written and maintained as Markdown files in `report/chapters/`. Python build scripts (`build_reports_docx.py`, `build_reports_pptx.py`, `build_exec_decks.py`) assemble formatted outputs from the Markdown source. Word and PPTX files are treated as derived artefacts: never edited by hand, always regenerated from source.

## Consequences

Better: Markdown diffs in PRs are human-readable; chapters can be reviewed line by line; any formatted output can be regenerated from a clean source at any time.

Worse: build scripts must handle all formatting concerns (section order, abbreviation expansion, headers/footers); initial setup cost higher than just writing in Word directly.

Watch for: abbreviation first-use tracking across chapters (handled by `expand_acronyms.py`); chapter ordering must be explicit in build scripts.
