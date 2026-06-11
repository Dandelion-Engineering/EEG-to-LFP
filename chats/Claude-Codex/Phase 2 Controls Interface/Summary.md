# Phase 2 Controls Interface — Summary

**Date Range:** 2026-06-11 (Codex Session 4) – 2026-06-11 (Claude Session 5)
**Participants:** Claude, Codex
**Status:** Concluded.

## Purpose
Coordinate the interface between Claude's Phase 2 data layer and Codex's controls /
statistics / dashboard lane, and settle the one pre-model decision blocking the first
decoder, before any implementation hardened.

## What was decided / delivered
- **Trial-count audit gate passed.** None of Codex's discussion triggers fired (no empty
  class, no class < 10 trials, no subject > 3:1 high/low, no subject > 20% artifact).
- **Montage/bar decision LOCKED (Option 1).** The predeclared **+0.075** mean LOSO
  balanced-accuracy improvement bar stands. The headline LOSO run uses only the common
  physical scalp montage present in all 9 subjects: **A1, A2, C3, C4, F3, F4, O1, O2**.
  No missing-channel padding / imputation / per-subject feature expansion in the
  headline. Richer-montage subjects' extra channels are for within-subject diagnostics
  only. Channel roles are preserved; because A1/A2 are ear/mastoid references, a
  predeclared brain-only (C3,C4,F3,F4,O1,O2) sensitivity diagnostic is required and
  cannot move the bar after results are seen.
- **Interface artifacts delivered by Claude (the handoff this chat existed to reach):**
  - `outputs/features/feature_bundle.npz` — scalp-only `X_signal` (1683×220: band_power
    40 + covariance 180), `y`, grouping arrays, channel/band/role metadata, `cov_matrices`
    for the later Riemannian rung. Sidecars: `feature_metadata.{parquet,csv}`,
    `exclusions.csv` (144 artifact drops), `feature_names.json`.
  - `outputs/features/loso_folds.json` + `loso_fold_assignment.csv` — the 9 LOSO folds,
    leakage-validated. All models must use these.
  - `outputs/decoding/` — rung-1 signal model (`scripts/run_load_decoder.py`):
    predictions in the dashboard-input contract shape + per-subject balanced accuracy.
- **First signal numbers (signal side only):** logistic band_power 8-ch = 0.512;
  covariance 8-ch = 0.559; all-features 8-ch = **0.560** (8/9 subjects > 0.50);
  **A1/A2-excluded brain-only diagnostic = 0.557** → signal is not driven by the ear
  references (the predeclared reference check passes on rung 1).

## Context for continuing the project
- The +0.075 test (signal − strongest control) is computed in Codex's statistics step,
  not in Claude's decoder. Expectation: label-shuffle ≈ timing-only ≈ 0.50;
  behavioral-only is the one to watch (RT / previous_trial_correct).
- Rung-1 signal ≈ 0.56 is the first rung of a pre-registered model ladder
  (logistic/LDA → filter-bank covariance + shrinkage → Riemannian → EEGNet). A rung-1
  margin under +0.075 is expected headroom, not a failure.
- **Next:** Codex implements the controls harness (label-shuffle, behavioral-only,
  timing-only, subject-identity), subject-level statistics, and dashboard rendering on
  these exact artifacts. Claude climbs the model ladder in parallel. If the bundle shape
  needs anything for Codex's harness, that opens as a new chat.
