"""
First-use acronym expansion across report chapters.

For each report, read the master abbreviations list (report*-00-abbreviations.md),
then walk the chapters in build order. The FIRST time each acronym appears in the
report (outside the abbreviations file, references sections, and URLs), spell it
out as "Full Form (ACRO)". If the first appearance is already an expansion
"...(ACRO)", leave it and just mark the acronym as defined.

Run with --apply to write changes; default is a dry run that prints proposals.
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
CH = BASE / "report" / "chapters"
APPLY = "--apply" in sys.argv

# Acronyms defined specially in-text (dash glosses) or proper names — never auto-expand.
SKIP = {"ATMs", "Umeme"}


def clean_full(form):
    # drop trailing/parenthetical glosses like "(sponge iron)" for inline use
    form = re.sub(r'\s*\([^)]*\)', '', form).strip()
    return form


def load_map(abbr_file):
    pairs = []
    for line in abbr_file.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', line)
        if not m:
            continue
        acro, full = m.group(1).strip(), m.group(2).strip()
        if acro.lower() == "abbreviation" or set(acro) <= {"-", ":"}:
            continue
        if acro in SKIP:
            continue
        pairs.append((acro, clean_full(full)))
    # longer acronyms first so "NDP IV" matches before a hypothetical "NDP"
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs


def ref_line_flags(lines):
    """Mark lines to skip: inside a References section, or containing a URL."""
    flags = [False] * len(lines)
    in_refs = False
    for i, ln in enumerate(lines):
        if re.match(r'^#+\s*References?\b', ln.strip(), re.I):
            in_refs = True
        elif re.match(r'^#+\s', ln.strip()):
            in_refs = False
        if in_refs or "http" in ln:
            flags[i] = True
    return flags


def is_clean(ln, start):
    """A 'clean' occurrence: in running text, not inside parentheses and not
    glued into a / - compound, so an inline expansion reads naturally."""
    before = ln[start - 1] if start > 0 else " "
    if before in "(/-–—.·":
        return False
    # inside an unclosed parenthesis on this line?
    head = ln[:start]
    if head.count("(") > head.count(")"):
        return False
    return True


def process(glob):
    files = [f for f in sorted(CH.glob(glob)) if "-00-" not in f.name]
    abbr = next(f for f in sorted(CH.glob(glob)) if "-00-" in f.name)
    mapping = load_map(abbr)

    docs = {f: f.read_text(encoding="utf-8").splitlines() for f in files}
    skipflags = {f: ref_line_flags(docs[f]) for f in files}
    # body text used only to detect existing "(ACRO)" author definitions
    body = "\n".join(
        ln for f in files for i, ln in enumerate(docs[f]) if not skipflags[f][i]
    )
    proposals = []

    for acro, full in mapping:
        # already spelled out by the author somewhere, e.g. "Authority (UIA)"?
        if re.search(r'\(' + re.escape(acro) + r'\)', body):
            continue
        pat = re.compile(r'(?<!\w)' + re.escape(acro) + r'(?!\w)')
        done = False
        for f in files:
            if done:
                break
            lines = docs[f]
            for i, ln in enumerate(lines):
                if skipflags[f][i]:
                    continue
                m = pat.search(ln)
                if not m or not is_clean(ln, m.start()):
                    continue
                expansion = f"{full} ({acro})"
                newln = ln[:m.start()] + expansion + ln[m.end():]
                proposals.append((f.name, acro, ln.strip(), newln.strip()))
                lines[i] = newln
                done = True
                break

    return files, docs, proposals


def main():
    for glob in ("report1-*.md", "report2-*.md"):
        files, docs, proposals = process(glob)
        print(f"\n===== {glob}  ({len(proposals)} expansions) =====")
        for name, acro, before, after in proposals:
            print(f"\n[{name}] {acro}")
            print(f"  -  {before[:160]}")
            print(f"  +  {after[:160]}")
        if APPLY:
            for f, lines in docs.items():
                f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nAPPLIED" if APPLY else "\nDRY RUN (no files changed) — re-run with --apply")


if __name__ == "__main__":
    main()
