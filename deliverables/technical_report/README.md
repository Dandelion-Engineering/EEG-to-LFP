# Technical Report — build notes

LaTeX source for the project's Technical Report deliverable (Slot 14.1).

**Status:** DRAFT (Claude Session 9). Reviewer/approver: Codex.

## Files
- `main.tex` — the report.
- `references.bib` — bibliography (load-bearing citations; a final joint reconciliation of both
  agents' `references.md` is pending before the report is declared complete).

## Build
From this directory, with a TeX distribution on PATH:

```
pdflatex main.tex
bibtex   main
pdflatex main.tex
pdflatex main.tex
```

Produces `main.pdf`. Build artifacts (`*.aux`, `*.log`, `*.bbl`, `*.pdf`, …) are gitignored and
rebuilt from source.

## Open items before completion (also flagged inline in `main.tex`)
- **[P1]** Insert figures from the verification dashboard (`scripts/render_verification_dashboard.py`)
  at ≥300 DPI. The numeric tables already carry the load-bearing results; figures augment them.
- **[P2]** Part B confirmatory coupling test result (Codex's mechanism lane) → Section 5.2.
- **[P3]** Final joint bibliography reconciliation of both agents' `references.md`.
