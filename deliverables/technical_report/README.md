# Technical Report - build notes

LaTeX source for the project's Technical Report deliverable (Slot 14.1).

**Status:** SOURCE APPROVED by Codex Session 13 on 2026-06-12. Local PDF compilation is still
blocked by the MiKTeX installation, not by a known report-source error.

## Files
- `main.tex` - the report.
- `references.bib` - bibliography; joint reconciliation of both agents' `references.md` complete
  (Claude Session 10, [P3]) and approved by Codex as reviewer.
- `figures/` - 300-DPI dashboard-derived PNGs exported by
  `scripts/export_dashboard_report_figures.py`.

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
- None currently tracked in this report README. The broader project still needs final
  Reproducibility Packet validation/approval before Phase 3 can close.

## Completed After Initial Draft
- **[P2]** Part B confirmatory coupling gate was run by Codex and inserted into Section 5.2.
  The gate failed, so Part B remains exploratory/inconclusive.
- **[P3]** Joint bibliography reconciliation of both agents' `references.md` (Claude Session 10).
  All `\cite` keys present with verified DOIs; both files cross-checked; Codex approved.
- **[P1]** Dashboard-derived report figures exported at 300 DPI and inserted into `main.tex`
  (Codex Session 12).
- **Report source approval** Codex Session 13 checked citation keys, figure paths, packet/report
  consistency, and the source status. `pdflatex` remains blocked before reading the source because
  MiKTeX cannot rebuild `pdflatex.fmt` (`formats.ini` missing plus lock-path permission failure).
