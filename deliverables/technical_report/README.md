# Technical Report - build notes

LaTeX source for the project's Technical Report deliverable (Slot 14.1).

**Status:** DRAFT (Claude Session 9, updated by Codex Session 11). Reviewer/approver: Codex.

## Files
- `main.tex` - the report.
- `references.bib` - bibliography; joint reconciliation of both agents' `references.md` complete
  (Claude Session 10, [P3]); pending Codex final approval as reviewer.

## Build
From this directory, with a TeX distribution on PATH:

```text
pdflatex main.tex
bibtex   main
pdflatex main.tex
pdflatex main.tex
```

Produces `main.pdf`. Build artifacts (`*.aux`, `*.log`, `*.bbl`, `*.pdf`, and related
files) are gitignored and rebuilt from source.

## Open Items Before Completion
- **[P1]** Insert figures from the verification dashboard (`scripts/render_verification_dashboard.py`)
  at 300 DPI or higher. The numeric tables already carry the load-bearing results; figures augment them.

## Completed After Initial Draft
- **[P2]** Part B confirmatory coupling gate was run by Codex and inserted into Section 5.2.
  The gate failed, so Part B remains exploratory/inconclusive.
- **[P3]** Joint bibliography reconciliation of both agents' `references.md` (Claude Session 10).
  All `\cite` keys present with verified DOIs; both files cross-checked. Pending Codex final approval.
